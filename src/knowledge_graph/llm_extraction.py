"""LLM-based assertion extraction for hypothesis scoring."""

from __future__ import annotations

import logging
import time
from pathlib import Path

import requests

from knowledge_graph.llm_client import call_ollama, parse_llm_response
from knowledge_graph.llm_config import LLMConfig
from knowledge_graph.llm_prompts import build_prompt, hypothesis_dicts, prompt_version
from knowledge_graph.nanopublication import (
    Assertion,
    Nanopublication,
    append_nanopubs,
    create_nanopub,
    deserialize_nanopubs,
    get_processed_paper_ids,
)
from knowledge_graph.provenance import ExtractionProvenance, new_run_id
from literature.models import Paper

logger = logging.getLogger(__name__)

_VALID_DIRECTIONS = {"supports", "contradicts", "neutral", "irrelevant"}
_VALID_EVIDENCE_STATUS = {"explicit_claim", "mentions", "no_evidence"}
_VALID_EVIDENCE_TYPE = {"theoretical", "empirical", "none"}

# Backward-compatible private aliases used by tests
_call_ollama = call_ollama
_parse_llm_response = parse_llm_response
_hypothesis_dicts = hypothesis_dicts


_WORD_CONFIDENCE = {
    "certain": 0.95,
    "very high": 0.9,
    "high": 0.8,
    "moderate": 0.6,
    "medium": 0.6,
    "fair": 0.5,
    "low": 0.4,
    "very low": 0.2,
    "none": 0.0,
    "unknown": 0.5,
}


def _parse_confidence(value: object) -> float:
    """Coerce an LLM confidence value to a float in [0, 1].

    gemma3:4b and similar small models sometimes return a word ("high") or a
    percentage ("80%") instead of a number. Rather than let one malformed field
    abort a whole paper's extraction, map words to values, strip ``%``/``~``,
    and fall back to a neutral 0.5 for anything unparseable.
    """
    if isinstance(value, bool):
        return 0.5
    if isinstance(value, (int, float)):
        # Bare numbers are already in [0, 1]; out-of-range values are clamped.
        return max(0.0, min(1.0, float(value)))
    text = str(value).strip().lower()
    if not text:
        return 0.5
    if text in _WORD_CONFIDENCE:
        return _WORD_CONFIDENCE[text]
    is_percent = "%" in text
    cleaned = text.replace("%", "").replace("~", "").strip()
    try:
        num = float(cleaned)
    except ValueError:
        return _WORD_CONFIDENCE.get(text.split()[0], 0.5)
    if is_percent:  # e.g. "80%" -> 0.8
        num = num / 100.0
    return max(0.0, min(1.0, num))


def _normalize_evidence_status(value: str) -> str:
    if value in _VALID_EVIDENCE_STATUS:
        return value
    return "mentions"


def _normalize_evidence_type(value: str) -> str:
    if value in _VALID_EVIDENCE_TYPE:
        return value
    return "none"


def assess_paper_hypotheses(
    paper: Paper,
    config: LLMConfig,
    *,
    run_id: str | None = None,
    pipeline_version: str = "2.0.3",
    _metrics: dict | None = None,
) -> list[tuple[Assertion, ExtractionProvenance]]:
    """Assess a single paper against all hypotheses via LLM."""
    hypotheses = hypothesis_dicts()
    prompt = build_prompt(paper, hypotheses)
    valid_hyp_ids = {h["id"] for h in hypotheses}
    last_error: Exception | None = None
    paper_t0 = time.monotonic()
    extraction_run_id = run_id or new_run_id()

    for attempt in range(1, config.max_retries + 1):
        try:
            raw, _meta = call_ollama(prompt, config)
            assessments = parse_llm_response(raw)
            results: list[tuple[Assertion, ExtractionProvenance]] = []
            n_filtered = 0
            for item in assessments:
                hyp_id = item.get("hypothesis_id", "")
                direction = item.get("direction", "irrelevant")
                reasoning = item.get("reasoning", "")
                if hyp_id not in valid_hyp_ids or direction not in _VALID_DIRECTIONS:
                    continue
                if direction == "irrelevant":
                    continue
                confidence = _parse_confidence(item.get("confidence", 0.0))
                if confidence < config.min_confidence:
                    n_filtered += 1
                    continue

                source_claim = item.get("source_claim_text", reasoning)
                evidence_quote = item.get("evidence_quote", "")
                evidence_status = _normalize_evidence_status(
                    item.get("evidence_status", "mentions")
                )
                evidence_type = _normalize_evidence_type(
                    item.get("evidence_type", "none")
                )

                assertion = Assertion(
                    assertion_id=f"llm_{paper.canonical_id}_{hyp_id}",
                    paper_id=paper.canonical_id,
                    claim=reasoning or f"LLM triage: {direction}",
                    assertion_type=direction,
                    hypothesis_id=hyp_id,
                    confidence=confidence,
                    citation_count=paper.citation_count,
                    source_claim_text=source_claim,
                    evidence_quote=evidence_quote,
                    evidence_status=evidence_status,
                    evidence_type=evidence_type,
                )
                provenance = ExtractionProvenance.create(
                    paper_id=paper.canonical_id,
                    source_passage=evidence_quote or (paper.abstract or "")[:512],
                    model_id=config.model,
                    llm_url=config.base_url,
                    pipeline_version=pipeline_version,
                    run_id=extraction_run_id,
                )
                results.append((assertion, provenance))

            if _metrics is not None:
                _metrics["filtered_total"] = _metrics.get("filtered_total", 0) + n_filtered
            logger.info(
                "  ✓ %s | %d assertions (%.1fs)",
                paper.title[:60],
                len(results),
                time.monotonic() - paper_t0,
            )
            return results
        except (ValueError, requests.RequestException, KeyError) as exc:
            last_error = exc
            logger.warning(
                "LLM extraction attempt %d/%d failed for %s: %s",
                attempt,
                config.max_retries,
                paper.canonical_id[:40],
                exc,
            )
            if attempt < config.max_retries:
                time.sleep(config.retry_delay * (2 ** (attempt - 1)))

    raise RuntimeError(
        f"LLM extraction failed after {config.max_retries} retries "
        f"for paper {paper.canonical_id}: {last_error}"
    )


def extract_assertions_llm(
    papers: list[Paper],
    config: LLMConfig | None = None,
    *,
    run_id: str | None = None,
    pipeline_version: str = "2.0.3",
) -> list[Assertion]:
    """Extract assertions from all papers using an LLM."""
    if config is None:
        config = LLMConfig()

    extraction_run_id = run_id or new_run_id()
    papers_with_abstract = [p for p in papers if p.abstract]
    logger.info(
        "Starting LLM extraction: %d papers (%d with abstracts), model=%s, url=%s, prompt=%s",
        len(papers),
        len(papers_with_abstract),
        config.model,
        config.base_url,
        prompt_version(),
    )

    nanopub_path = Path(config.nanopub_path) if config.nanopub_path else None
    if nanopub_path:
        logger.info("Nanopub persistence file: %s", nanopub_path)
    if config.max_papers is not None:
        logger.info(
            "max_papers=%d — will process at most %d papers",
            config.max_papers,
            config.max_papers,
        )

    processed_ids: set[str] = set()
    prior_assertions: list[Assertion] = []

    if nanopub_path and nanopub_path.exists():
        existing_nanopubs = deserialize_nanopubs(nanopub_path)
        processed_ids = get_processed_paper_ids(existing_nanopubs)
        prior_assertions = [np_obj.assertion for np_obj in existing_nanopubs]
        if processed_ids:
            remaining = sum(
                1
                for p in papers
                if p.canonical_id not in processed_ids and p.abstract
            )
            logger.info(
                "Resuming: %d papers already processed (%d assertions), "
                "%d remaining | nanopub_path: %s",
                len(processed_ids),
                len(prior_assertions),
                remaining,
                nanopub_path,
            )
    elif nanopub_path:
        logger.info("Fresh run — nanopubs will be saved to: %s", nanopub_path)

    buffer: list[Nanopublication] = []
    new_assertions: list[Assertion] = []
    filter_metrics: dict[str, int] = {"filtered_total": 0}
    new_count = 0
    success_count = 0
    fail_count = 0
    t0 = time.monotonic()
    attribution = f"pipeline_{pipeline_version}:{prompt_version()}"

    for paper in papers:
        if not paper.abstract or paper.canonical_id in processed_ids:
            continue
        if config.max_papers is not None and new_count >= config.max_papers:
            logger.info("max_papers=%d reached — stopping extraction early", config.max_papers)
            break
        try:
            pairs = assess_paper_hypotheses(
                paper,
                config,
                run_id=extraction_run_id,
                pipeline_version=pipeline_version,
                _metrics=filter_metrics,
            )
            for assertion, provenance in pairs:
                new_assertions.append(assertion)
                buffer.append(
                    create_nanopub(
                        assertion,
                        attribution=attribution,
                        provenance=provenance.to_dict(),
                    )
                )
            processed_ids.add(paper.canonical_id)
            success_count += 1
            new_count += 1
        except RuntimeError as exc:
            logger.error("  ✗ Failed %s: %s", paper.canonical_id[:40], exc)
            fail_count += 1
            new_count += 1

        if (
            nanopub_path
            and new_count > 0
            and new_count % config.checkpoint_interval == 0
            and buffer
        ):
            append_nanopubs(buffer, nanopub_path)
            buffer.clear()

    if nanopub_path and buffer:
        append_nanopubs(buffer, nanopub_path)
        logger.info("Nanopublications saved: %s (%d new)", nanopub_path, len(buffer))

    logger.info(
        "LLM extraction complete: %d succeeded, %d failed, %d assertions (%.1fs)",
        success_count,
        fail_count,
        len(prior_assertions) + len(new_assertions),
        time.monotonic() - t0,
    )
    return prior_assertions + new_assertions


__all__ = [
    "LLMConfig",
    "assess_paper_hypotheses",
    "build_prompt",
    "extract_assertions_llm",
    "_call_ollama",
    "_hypothesis_dicts",
    "_parse_llm_response",
]
