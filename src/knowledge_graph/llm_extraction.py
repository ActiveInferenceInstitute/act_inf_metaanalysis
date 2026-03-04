"""LLM-based assertion extraction for hypothesis scoring.

Sends paper abstracts to a configurable LLM (default: Ollama) and
receives structured assessments of each hypothesis. The LLM returns
a direction (supports/contradicts/neutral/irrelevant), a confidence
score, and a brief reasoning string for each hypothesis.

Configuration is via the :class:`LLMConfig` dataclass; the default
points to a local Ollama instance at ``http://localhost:11434``.

Persistence is **incremental**: assertions are flushed to the
``nanopub_path`` JSONL file every ``checkpoint_interval`` papers via
:func:`~knowledge_graph.nanopublication.append_nanopubs`.  On
restart, already-persisted paper IDs are skipped automatically.

Requires no additional dependencies beyond ``requests`` (already in
the project's dependency list).
"""

from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import requests

from knowledge_graph.nanopublication import (
    Assertion,
    Nanopublication,
    create_nanopub,
    append_nanopubs,
    deserialize_nanopubs,
    get_processed_paper_ids,
)
from knowledge_graph.hypothesis import HYPOTHESES
from literature.models import Paper

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

@dataclass
class LLMConfig:
    """Configuration for the LLM-based extraction backend.

    Attributes:
        base_url: Ollama (or compatible) API base URL.
        model: Model name to use for generation.
        temperature: Sampling temperature (0 = deterministic).
        max_tokens: Maximum tokens in the response.
        timeout_seconds: HTTP request timeout per paper.
        max_retries: Retries on transient / parse failures.
        retry_delay: Base delay between retries (seconds).
        nanopub_path: Path to nanopublications JSONL file for
            incremental persistence and resume.  ``None`` disables
            on-disk checkpointing (assertions are returned in-memory
            only).
        checkpoint_interval: Flush to disk every N papers.
        max_papers: Maximum number of papers to process.
            ``None`` means no limit (process all papers).
    """

    base_url: str = "http://localhost:11434"
    model: str = "gemma3:4b"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout_seconds: int = 120
    max_retries: int = 3
    retry_delay: float = 2.0
    nanopub_path: str | None = None
    checkpoint_interval: int = 50
    max_papers: int | None = None


# ---------------------------------------------------------------------------
# Prompt construction
# ---------------------------------------------------------------------------

_SYSTEM_PROMPT = """\
You are a scientific literature analyst specialising in Active Inference \
and the Free Energy Principle. You will receive a paper's title and \
abstract, together with a list of research hypotheses. For each \
hypothesis, assess whether the paper provides evidence that supports, \
contradicts, or is neutral toward the hypothesis, or whether the paper \
is irrelevant to it.

Return ONLY a JSON array (no markdown fences, no commentary). Each \
element must be an object with exactly these keys:

  "hypothesis_id"  – the ID string provided
  "direction"      – one of "supports", "contradicts", "neutral", "irrelevant"
  "confidence"     – a float in [0.0, 1.0] reflecting how strong the evidence is
  "reasoning"      – one sentence justifying the assessment

Example output:
[
  {"hypothesis_id": "FEP_UNIVERSALITY", "direction": "supports", "confidence": 0.8, "reasoning": "The paper provides formal proofs extending FEP to non-equilibrium systems."},
  {"hypothesis_id": "AIF_OPTIMALITY", "direction": "irrelevant", "confidence": 0.0, "reasoning": "The paper does not address planning or decision-making."}
]
"""


def build_prompt(paper: Paper, hypotheses: list[dict[str, str]]) -> str:
    """Build the user-turn prompt for a single paper.

    Args:
        paper: Paper whose abstract will be assessed.
        hypotheses: List of dicts with ``id``, ``name``, ``description``.

    Returns:
        Formatted prompt string.
    """
    hyp_block = "\n".join(
        f"  - {h['id']}: {h['name']} — {h['description']}"
        for h in hypotheses
    )
    return (
        f"## Paper\n"
        f"**Title:** {paper.title}\n"
        f"**Abstract:** {paper.abstract}\n\n"
        f"## Hypotheses to assess\n{hyp_block}\n\n"
        f"Respond with the JSON array now."
    )


def _hypothesis_dicts() -> list[dict[str, str]]:
    """Convert HYPOTHESES to simple dicts for the prompt."""
    return [
        {
            "id": h.hypothesis_id,
            "name": h.name,
            "description": h.description,
        }
        for h in HYPOTHESES
    ]


# ---------------------------------------------------------------------------
# LLM API interaction
# ---------------------------------------------------------------------------

def _call_ollama(
    prompt: str,
    config: LLMConfig,
) -> tuple[str, dict]:
    """Send a prompt to the Ollama /api/generate endpoint.

    Args:
        prompt: The full user prompt.
        config: LLM configuration.

    Returns:
        Tuple of (response_text, metadata_dict).  Metadata contains
        ``prompt_chars``, ``response_chars``, ``eval_duration_s``, and
        ``tokens_per_s`` when available.

    Raises:
        requests.HTTPError: On non-2xx responses.
        requests.Timeout: On timeout.
    """
    url = f"{config.base_url}/api/generate"
    payload = {
        "model": config.model,
        "prompt": prompt,
        "system": _SYSTEM_PROMPT,
        "stream": False,
        "options": {
            "temperature": config.temperature,
            "num_predict": config.max_tokens,
        },
    }

    resp = requests.post(url, json=payload, timeout=config.timeout_seconds)
    resp.raise_for_status()

    data = resp.json()
    response_text = data.get("response", "")

    # Extract Ollama-provided timing metadata
    eval_duration_ns = data.get("eval_duration", 0)
    eval_count = data.get("eval_count", 0)
    eval_duration_s = eval_duration_ns / 1e9 if eval_duration_ns else 0
    tokens_per_s = (eval_count / eval_duration_s) if eval_duration_s > 0 else 0

    meta = {
        "prompt_chars": len(prompt),
        "response_chars": len(response_text),
        "eval_duration_s": round(eval_duration_s, 2),
        "tokens_per_s": round(tokens_per_s, 1),
        "eval_count": eval_count,
    }
    return response_text, meta


def _parse_llm_response(raw: str) -> list[dict[str, Any]]:
    """Parse the LLM's JSON array response.

    Handles common issues: markdown code fences, trailing commas,
    and text before/after the JSON array.

    Args:
        raw: Raw text response from the LLM.

    Returns:
        Parsed list of assessment dicts.

    Raises:
        ValueError: If parsing fails after cleanup attempts.
    """
    text = raw.strip()

    # Strip markdown code fences if present
    if text.startswith("```"):
        # Remove opening fence (possibly with language tag)
        first_newline = text.index("\n")
        text = text[first_newline + 1:]
    if text.endswith("```"):
        text = text[:-3].rstrip()

    # Find the JSON array bounds
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1 or end <= start:
        raise ValueError(f"No JSON array found in LLM response: {text[:200]}")

    json_str = text[start : end + 1]

    try:
        result = json.loads(json_str)
    except json.JSONDecodeError as e:
        raise ValueError(f"Failed to parse JSON from LLM response: {e}") from e

    if not isinstance(result, list):
        raise ValueError(f"Expected JSON array, got {type(result).__name__}")

    return result


# ---------------------------------------------------------------------------
# Single-paper assessment
# ---------------------------------------------------------------------------

_VALID_DIRECTIONS = {"supports", "contradicts", "neutral", "irrelevant"}


def assess_paper_hypotheses(
    paper: Paper,
    config: LLMConfig,
) -> list[Assertion]:
    """Assess a single paper against all 8 hypotheses via LLM.

    Args:
        paper: Paper to assess.
        config: LLM configuration.

    Returns:
        List of Assertion objects (excluding ``irrelevant`` assessments).

    Raises:
        RuntimeError: If all retries are exhausted.
    """
    hypotheses = _hypothesis_dicts()
    prompt = build_prompt(paper, hypotheses)
    valid_hyp_ids = {h["id"] for h in hypotheses}

    last_error: Exception | None = None
    paper_t0 = time.monotonic()

    for attempt in range(1, config.max_retries + 1):
        try:
            raw, meta = _call_ollama(prompt, config)
            assessments = _parse_llm_response(raw)

            assertions: list[Assertion] = []
            direction_counts: dict[str, int] = {}
            for i, item in enumerate(assessments):
                hyp_id = item.get("hypothesis_id", "")
                direction = item.get("direction", "irrelevant")
                confidence = float(item.get("confidence", 0.0))
                reasoning = item.get("reasoning", "")

                # Validate
                if hyp_id not in valid_hyp_ids:
                    logger.debug(
                        "Skipping unknown hypothesis_id %r from LLM", hyp_id
                    )
                    continue
                if direction not in _VALID_DIRECTIONS:
                    logger.debug(
                        "Skipping invalid direction %r for %s", direction, hyp_id
                    )
                    continue
                if direction == "irrelevant":
                    continue

                direction_counts[direction] = direction_counts.get(direction, 0) + 1

                # Clamp confidence
                confidence = max(0.0, min(1.0, confidence))

                assertions.append(
                    Assertion(
                        assertion_id=f"llm_{paper.canonical_id}_{hyp_id}",
                        paper_id=paper.canonical_id,
                        claim=reasoning or f"LLM assessment: {direction}",
                        assertion_type=direction,
                        hypothesis_id=hyp_id,
                        confidence=confidence,
                        citation_count=paper.citation_count,
                    )
                )

            paper_elapsed = time.monotonic() - paper_t0
            title_short = (paper.title[:60] + "...") if len(paper.title) > 63 else paper.title
            dir_summary = ", ".join(f"{k}={v}" for k, v in sorted(direction_counts.items()))
            logger.info(
                "  ✓ %s | in=%dch out=%dch | %.1fs %.1ftok/s | "
                "%d assertions (%s)",
                title_short,
                meta.get("prompt_chars", 0),
                meta.get("response_chars", 0),
                paper_elapsed,
                meta.get("tokens_per_s", 0),
                len(assertions),
                dir_summary or "none",
            )
            return assertions

        except (ValueError, requests.RequestException, KeyError) as exc:
            last_error = exc
            logger.warning(
                "LLM extraction attempt %d/%d failed for %s: %s",
                attempt, config.max_retries, paper.canonical_id[:40], exc,
            )
            if attempt < config.max_retries:
                delay = config.retry_delay * (2 ** (attempt - 1))
                time.sleep(delay)

    raise RuntimeError(
        f"LLM extraction failed after {config.max_retries} retries "
        f"for paper {paper.canonical_id}: {last_error}"
    )


# ---------------------------------------------------------------------------
# Batch extraction (with incremental nanopub persistence)
# ---------------------------------------------------------------------------

def extract_assertions_llm(
    papers: list[Paper],
    config: LLMConfig | None = None,
) -> list[Assertion]:
    """Extract assertions from all papers using an LLM.

    Processes papers sequentially with rich per-paper logging. Papers that
    fail after all retries are logged and skipped (the pipeline
    continues).

    **Incremental persistence:** When ``config.nanopub_path`` is set,
    already-processed papers (present in the nanopubs file) are skipped.
    New assertions are flushed to the same file every
    ``config.checkpoint_interval`` papers via
    :func:`~knowledge_graph.nanopublication.append_nanopubs`, ensuring
    that interrupted runs lose at most one checkpoint interval of work.

    Args:
        papers: Papers to analyse.
        config: LLM configuration (uses defaults if ``None``).

    Returns:
        Aggregated list of Assertion objects across all papers
        (including both previously-persisted and newly-extracted).
    """
    if config is None:
        config = LLMConfig()

    papers_with_abstract = [p for p in papers if p.abstract]
    logger.info(
        "Starting LLM extraction: %d papers (%d with abstracts), "
        "model=%s, url=%s",
        len(papers), len(papers_with_abstract),
        config.model, config.base_url,
    )
    if config.nanopub_path:
        logger.info("📄 Nanopub persistence file: %s", config.nanopub_path)
    if config.max_papers is not None:
        logger.info("🔒 max_papers=%d — will process at most %d papers",
                     config.max_papers, config.max_papers)

    # --- Resume: load already-processed paper IDs from nanopub file ---
    nanopub_path = Path(config.nanopub_path) if config.nanopub_path else None
    processed_ids: set[str] = set()
    prior_assertions: list[Assertion] = []

    if nanopub_path and nanopub_path.exists():
        existing_nanopubs = deserialize_nanopubs(nanopub_path)
        processed_ids = get_processed_paper_ids(existing_nanopubs)
        prior_assertions = [np_obj.assertion for np_obj in existing_nanopubs]
        if processed_ids:
            remaining = sum(
                1 for p in papers
                if p.canonical_id not in processed_ids and p.abstract
            )
            logger.info(
                "Resuming: %d papers already processed (%d assertions), "
                "%d remaining | nanopub_path: %s",
                len(processed_ids), len(prior_assertions),
                remaining, nanopub_path,
            )
    elif nanopub_path:
        logger.info("📄 Fresh run — nanopubs will be saved to: %s", nanopub_path)

    # --- Process new papers ---
    success_count = len(processed_ids)
    fail_count = 0
    new_count = 0
    buffer: list[Nanopublication] = []  # unflushed nanopubs
    new_assertions: list[Assertion] = []
    t0 = time.monotonic()

    for idx, paper in enumerate(papers, 1):
        if not paper.abstract:
            logger.debug("Skipping paper %s (no abstract)", paper.canonical_id[:30])
            continue

        # Skip already-processed papers (resume support)
        if paper.canonical_id in processed_ids:
            continue

        # Honour max_papers cap
        if config.max_papers is not None and new_count >= config.max_papers:
            logger.info(
                "🔒 max_papers=%d reached — stopping extraction early",
                config.max_papers,
            )
            break

        try:
            assertions = assess_paper_hypotheses(paper, config)
            new_assertions.extend(assertions)
            # Wrap as nanopubs for persistence
            for a in assertions:
                buffer.append(create_nanopub(a, attribution="pipeline_v1"))
            processed_ids.add(paper.canonical_id)
            success_count += 1
            new_count += 1
        except RuntimeError as exc:
            logger.error(
                "  ✗ Skipping %s: %s",
                paper.canonical_id[:40], exc,
            )
            processed_ids.add(paper.canonical_id)  # Don't retry on resume
            fail_count += 1
            new_count += 1

        # Progress logging every 10 papers
        if new_count % 10 == 0 or idx == len(papers):
            elapsed = time.monotonic() - t0
            rate = new_count / elapsed if elapsed > 0 else 0
            remaining_papers = sum(
                1 for p in papers
                if p.canonical_id not in processed_ids and p.abstract
            )
            eta_min = (remaining_papers / rate / 60) if rate > 0 else 0
            logger.info(
                "── Progress: %d/%d papers | %d assertions | "
                "%.2f papers/s | elapsed %.0fs | ETA ~%.0fm | "
                "%d failures | model=%s",
                success_count, len(papers_with_abstract),
                len(prior_assertions) + len(new_assertions),
                rate, elapsed, eta_min,
                fail_count, config.model,
            )

        # Flush buffer to nanopub file at configured interval
        if nanopub_path and new_count > 0 and new_count % config.checkpoint_interval == 0:
            append_nanopubs(buffer, nanopub_path)
            logger.info(
                "💾 Checkpoint flushed: %d new nanopubs → %s "
                "(total on disk: %d papers processed)",
                len(buffer), nanopub_path, success_count,
            )
            buffer.clear()

    # Final flush of remaining buffer
    if nanopub_path and buffer:
        append_nanopubs(buffer, nanopub_path)
        logger.info(
            "💾 Final flush: %d nanopubs → %s "
            "(total on disk: %d papers processed)",
            len(buffer), nanopub_path, success_count,
        )
        buffer.clear()

    elapsed = time.monotonic() - t0
    total_assertions = len(prior_assertions) + len(new_assertions)
    logger.info(
        "LLM extraction complete: %d papers succeeded, %d failed, "
        "%d assertions total (%.1fs, %.2f papers/s)",
        success_count, fail_count,
        total_assertions,
        elapsed, new_count / elapsed if elapsed > 0 else 0,
    )
    if nanopub_path:
        logger.info(
            "📄 Nanopublications saved: %s (%d assertions from %d papers)",
            nanopub_path, total_assertions, success_count,
        )

    return prior_assertions + new_assertions
