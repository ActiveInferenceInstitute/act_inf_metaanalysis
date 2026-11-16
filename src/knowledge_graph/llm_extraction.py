"""LLM-based assertion extraction for hypothesis scoring."""

from __future__ import annotations

import json
import logging
import time

import requests

from collections import deque
from concurrent.futures import CancelledError, Future, ThreadPoolExecutor
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from threading import Event
from typing import Any

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
from config import PIPELINE_VERSION
from literature.models import Paper

logger = logging.getLogger(__name__)

_VALID_DIRECTIONS = {"supports", "contradicts", "neutral", "irrelevant"}
_VALID_EVIDENCE_STATUS = {"explicit_claim", "mentions", "no_evidence"}
_VALID_EVIDENCE_TYPE = {"theoretical", "empirical", "none"}

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


def _write_extraction_state(path: Path | None, payload: dict[str, Any]) -> None:
    """Atomically publish a receipt after its nanopublications are durable."""
    if path is None:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, indent=2)
        handle.write("\n")
    temporary.replace(path)


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
    pipeline_version: str = PIPELINE_VERSION,
    _metrics: dict | None = None,
    _cancel_event: Event | None = None,
) -> list[tuple[Assertion, ExtractionProvenance]]:
    """Assess a single paper against all hypotheses via LLM."""
    hypotheses = hypothesis_dicts()
    prompt = build_prompt(paper, hypotheses)
    valid_hyp_ids = {h["id"] for h in hypotheses}
    last_error: Exception | None = None
    paper_t0 = time.monotonic()
    extraction_run_id = run_id or new_run_id()

    for attempt in range(1, config.max_retries + 1):
        if _cancel_event is not None and _cancel_event.is_set():
            raise CancelledError("Extraction interrupted")
        try:
            request_config = (
                replace(config, max_tokens=max(config.max_tokens, 2048), temperature=0.2)
                if attempt > 1
                else config
            )
            raw, _meta = call_ollama(prompt, request_config)
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
                delay = config.retry_delay * (2 ** (attempt - 1))
                if _cancel_event is None:
                    time.sleep(delay)
                elif _cancel_event.wait(delay):
                    raise CancelledError("Extraction interrupted") from exc

    raise RuntimeError(
        f"LLM extraction failed after {config.max_retries} retries "
        f"for paper {paper.canonical_id}: {last_error}"
    )


def extract_assertions_llm(
    papers: list[Paper],
    config: LLMConfig | None = None,
    *,
    run_id: str | None = None,
    pipeline_version: str = PIPELINE_VERSION,
) -> list[Assertion]:
    """Resume durable paper outcomes, including successful zero-assertion results."""
    if config is None:
        config = LLMConfig()
    papers_with_abstract = [paper for paper in papers if paper.abstract]
    logger.info(
        "Starting LLM extraction: %d papers (%d with abstracts), model=%s, url=%s, prompt=%s",
        len(papers), len(papers_with_abstract), config.model, config.base_url, prompt_version(),
    )
    nanopub_path = Path(config.nanopub_path) if config.nanopub_path else None
    state_path = nanopub_path.parent / "extraction_state.json" if nanopub_path else None
    coverage_path = nanopub_path.parent / "extraction_coverage.json" if nanopub_path else None
    if nanopub_path:
        logger.info("Nanopub persistence file: %s", nanopub_path)

    existing_nanopubs = (
        deserialize_nanopubs(nanopub_path)
        if nanopub_path is not None and nanopub_path.exists() else []
    )
    processed_ids = get_processed_paper_ids(existing_nanopubs)
    zero_assertion_ids: set[str] = set()
    prior_assertions = [record.assertion for record in existing_nanopubs]
    structured_provenance: list[dict[str, Any]] = [
        record.provenance for record in existing_nanopubs if record.provenance
    ]
    existing_run_ids = {
        str(item["run_id"]) for item in structured_provenance if item.get("run_id")
    }
    if state_path is not None and state_path.exists():
        try:
            state = json.loads(state_path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise RuntimeError(f"Cannot read extraction completion ledger: {state_path}") from exc
        if not isinstance(state, dict):
            raise RuntimeError("Extraction completion ledger must be an object")
        # Older count-only receipts cannot establish zero-assertion completion.
        if "completion_ledger_version" in state:
            if state["completion_ledger_version"] != 1:
                raise RuntimeError("Unsupported extraction completion ledger version")
            for field in ("processed_paper_ids", "zero_assertion_paper_ids"):
                values = state.get(field)
                if not isinstance(values, list) or any(
                    not isinstance(value, str) or not value for value in values
                ):
                    raise RuntimeError(f"Invalid completion ledger field: {field}")
            recorded_ids = set(state["processed_paper_ids"])
            zero_assertion_ids = set(state["zero_assertion_paper_ids"])
            if not zero_assertion_ids <= recorded_ids:
                raise RuntimeError("Zero-assertion outcomes are missing from completed paper IDs")
            if nanopub_path is None or not nanopub_path.is_file():
                raise RuntimeError("Completion ledger has no persisted nanopublication file")
            if recorded_ids - zero_assertion_ids - processed_ids:
                raise RuntimeError("Completion ledger refers to missing persisted assertions")
            recorded_run = state.get("run_id")
            if not isinstance(recorded_run, str) or not recorded_run:
                raise RuntimeError("Completion ledger has no extraction run ID")
            existing_run_ids.add(recorded_run)
            structured_provenance.append(state)
            zero_assertion_ids.difference_update(processed_ids)
            processed_ids.update(zero_assertion_ids)

    for field, expected in (
        ("model_id", config.model),
        ("prompt_version", prompt_version()),
        ("pipeline_version", pipeline_version),
    ):
        observed = {str(item.get(field, "")) for item in structured_provenance}
        if observed and observed != {expected}:
            raise RuntimeError(
                "Cannot resume nanopublications with incompatible "
                f"{field}: observed={sorted(observed)}, expected={expected}"
            )
    if len(existing_run_ids) > 1:
        raise RuntimeError(
            "Cannot resume nanopublications with multiple extraction run IDs: "
            f"{sorted(existing_run_ids)}"
        )
    if existing_run_ids:
        extraction_run_id = next(iter(existing_run_ids))
        if run_id is not None and run_id != extraction_run_id:
            raise RuntimeError(
                "Requested extraction run ID does not match the checkpoint: "
                f"{run_id} != {extraction_run_id}"
            )
        logger.info("Resuming extraction run ID: %s", extraction_run_id)
    else:
        extraction_run_id = run_id or new_run_id()

    eligible_ids = {paper.canonical_id for paper in papers_with_abstract}
    eligible_papers = [
        paper for paper in papers_with_abstract if paper.canonical_id not in processed_ids
    ]
    if processed_ids:
        logger.info(
            "Resuming: %d papers already processed (%d assertions), "
            "%d remaining | nanopub_path: %s",
            len(processed_ids), len(prior_assertions), len(eligible_papers), nanopub_path,
        )
    if config.max_papers is not None:
        eligible_papers = eligible_papers[: config.max_papers]
        logger.info(
            "max_papers=%d reached — stopping extraction early; processing at most %d papers",
            config.max_papers, len(eligible_papers),
        )

    buffer: list[Nanopublication] = []
    new_assertions: list[Assertion] = []
    failed_ids: set[str] = set()
    filter_metrics: dict[str, int] = {"filtered_total": 0}
    new_count = 0
    success_count = 0
    t0 = time.monotonic()
    attribution = f"pipeline_{pipeline_version}:{prompt_version()}"
    cancel_event = Event()

    def _coverage() -> dict[str, Any]:
        return {
            "total_papers": len(papers),
            "eligible_papers": len(eligible_ids),
            "processed_papers": len(eligible_ids & processed_ids),
            "failed_papers": len(eligible_ids & failed_ids),
            "unprocessed_papers": len(eligible_ids - processed_ids - failed_ids),
            "assertions": len(prior_assertions) + len(new_assertions),
            "model_id": config.model,
            "prompt_version": prompt_version(),
            "pipeline_version": pipeline_version,
            "run_id": extraction_run_id,
        }

    def _checkpoint(status: str) -> None:
        if nanopub_path is None:
            return
        # Publish assertion bytes first. A crash between these writes can only
        # require repeating a zero-result assessment, never invent completion.
        if buffer or not nanopub_path.exists():
            append_nanopubs(buffer, nanopub_path)
            logger.info("Nanopublications saved: %s (%d new)", nanopub_path, len(buffer))
            buffer.clear()
        coverage = {**_coverage(), "status": status}
        _write_extraction_state(state_path, {
            **coverage,
            "completion_ledger_version": 1,
            "processed_paper_ids": sorted(processed_ids),
            "zero_assertion_paper_ids": sorted(zero_assertion_ids),
            "checkpoint_interval": config.checkpoint_interval,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        })
        _write_extraction_state(coverage_path, coverage)

    worker_urls = tuple(config.worker_urls) or (config.base_url,)
    worker_configs = [replace(config, base_url=url, worker_urls=()) for url in worker_urls]
    logger.info("Extraction workers: %d (%s)", len(worker_configs), ", ".join(worker_urls))

    def _process(item: tuple[int, Paper]):
        index, paper = item
        metrics: dict[str, int] = {}
        try:
            pairs = assess_paper_hypotheses(
                paper, worker_configs[index % len(worker_configs)],
                run_id=extraction_run_id, pipeline_version=pipeline_version,
                _metrics=metrics, _cancel_event=cancel_event,
            )
            return paper, pairs, None, metrics
        except RuntimeError as exc:
            return paper, [], exc, metrics

    def _accept(result) -> None:
        nonlocal new_count, success_count
        paper, pairs, error, metrics = result
        filter_metrics["filtered_total"] += metrics.get("filtered_total", 0)
        if error is not None:
            logger.error("Failed %s: %s", paper.canonical_id[:40], error)
            if paper.canonical_id not in processed_ids:
                failed_ids.add(paper.canonical_id)
        else:
            records = [
                create_nanopub(assertion, attribution=attribution, provenance=provenance.to_dict())
                for assertion, provenance in pairs
            ]
            buffer.extend(records)
            new_assertions.extend(record.assertion for record in records)
            processed_ids.add(paper.canonical_id)
            failed_ids.discard(paper.canonical_id)
            if records:
                zero_assertion_ids.discard(paper.canonical_id)
            else:
                zero_assertion_ids.add(paper.canonical_id)
            success_count += 1
        new_count += 1

    _checkpoint("running")
    executor = (
        ThreadPoolExecutor(max_workers=len(worker_configs)) if len(worker_configs) > 1 else None
    )
    pending: deque[Future[Any]] = deque()
    try:
        if executor is None:
            for item in enumerate(eligible_papers):
                _accept(_process(item))
                if new_count % config.checkpoint_interval == 0:
                    _checkpoint("checkpoint")
        else:
            items = iter(enumerate(eligible_papers))
            # Never eagerly queue the corpus. At most one outstanding call per
            # configured worker remains to cancel or drain on interruption.
            for _ in worker_configs:
                next_item = next(items, None)
                if next_item is not None:
                    pending.append(executor.submit(_process, next_item))
            while pending:
                result = pending[0].result()
                pending.popleft()
                _accept(result)
                if new_count % config.checkpoint_interval == 0:
                    _checkpoint("checkpoint")
                next_item = next(items, None)
                if next_item is not None:
                    pending.append(executor.submit(_process, next_item))
    except KeyboardInterrupt:
        cancel_event.set()
        for future in pending:
            future.cancel()
        for future in pending:
            if future.done() and not future.cancelled():
                try:
                    _accept(future.result())
                except CancelledError:
                    pass
        _checkpoint("interrupted")
        logger.warning(
            "LLM extraction interrupted; resume without --clear-assertions "
            "to continue run ID %s from the paper completion ledger",
            extraction_run_id,
        )
        raise
    finally:
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=True)

    complete = not failed_ids and not (eligible_ids - processed_ids)
    _checkpoint("complete" if complete else "incomplete")
    logger.info(
        "LLM extraction complete: %d succeeded, %d failed, %d assertions (%.1fs)",
        success_count, len(failed_ids), len(prior_assertions) + len(new_assertions),
        time.monotonic() - t0,
    )
    return prior_assertions + new_assertions


__all__ = [
    "LLMConfig",
    "assess_paper_hypotheses",
    "build_prompt",
    "extract_assertions_llm",
]
