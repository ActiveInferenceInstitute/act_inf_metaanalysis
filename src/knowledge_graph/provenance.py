"""Structured extraction provenance for nanopublications."""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

from config import PROMPT_VERSION as CONFIG_PROMPT_VERSION

PROMPT_VERSION = CONFIG_PROMPT_VERSION


@dataclass
class ExtractionProvenance:
    """Lineage metadata for a single LLM extraction."""

    paper_id: str
    source_passage: str
    model_id: str
    llm_host: str
    prompt_version: str
    processing_date: str
    pipeline_version: str
    run_id: str
    source_section: str = "abstract"

    @classmethod
    def create(
        cls,
        *,
        paper_id: str,
        source_passage: str,
        model_id: str,
        llm_url: str,
        pipeline_version: str,
        run_id: str | None = None,
        source_section: str = "abstract",
        prompt_version: str = PROMPT_VERSION,
    ) -> ExtractionProvenance:
        host = urlparse(llm_url).netloc or llm_url
        return cls(
            paper_id=paper_id,
            source_passage=source_passage,
            model_id=model_id,
            llm_host=host,
            prompt_version=prompt_version,
            processing_date=datetime.now(timezone.utc).isoformat(),
            pipeline_version=pipeline_version,
            run_id=run_id or uuid.uuid4().hex,
            source_section=source_section,
        )

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


def new_run_id() -> str:
    """Generate a run identifier for one KG extraction stage."""
    return uuid.uuid4().hex


def summarize_provenance(records: list[dict[str, Any]]) -> dict[str, Any]:
    """Aggregate the structured provenance block across serialized nanopublications.

    Every nanopublication produced by the three-layer extractor carries a
    ``provenance`` block (model, prompt version, processing date, run id). This
    summary reports model/prompt coverage and the processing-date range, and
    flags any record missing a provenance block (which should never occur for a
    freshly extracted corpus).
    """
    if not records:
        return {"total": 0, "with_provenance": 0}

    models: dict[str, int] = {}
    prompts: dict[str, int] = {}
    pipelines: dict[str, int] = {}
    run_ids: set[str] = set()
    processing_dates: list[str] = []
    with_provenance = 0

    for record in records:
        prov = record.get("provenance")
        if not prov:
            continue
        with_provenance += 1
        models[prov.get("model_id", "unknown")] = (
            models.get(prov.get("model_id", "unknown"), 0) + 1
        )
        prompts[prov.get("prompt_version", "unknown")] = (
            prompts.get(prov.get("prompt_version", "unknown"), 0) + 1
        )
        pipelines[prov.get("pipeline_version", "unknown")] = (
            pipelines.get(prov.get("pipeline_version", "unknown"), 0) + 1
        )
        if prov.get("run_id"):
            run_ids.add(prov["run_id"])
        if prov.get("processing_date"):
            processing_dates.append(prov["processing_date"])

    total = len(records)
    return {
        "total": total,
        "with_provenance": with_provenance,
        "missing_provenance": total - with_provenance,
        "unique_models": models,
        "prompt_versions": prompts,
        "pipeline_versions": pipelines,
        "consistent_provenance": (
            with_provenance == total
            and len(models) == 1
            and len(prompts) == 1
            and len(pipelines) == 1
        ),
        "unique_run_ids": len(run_ids),
        "processing_date_range": (
            [min(processing_dates), max(processing_dates)] if processing_dates else []
        ),
    }


def write_provenance_summary(nanopub_path: Path, report_path: Path) -> dict[str, Any]:
    """Write ``extraction_provenance_summary.json`` from a nanopub JSONL file."""
    records: list[dict[str, Any]] = []
    if nanopub_path.exists():
        with open(nanopub_path, encoding="utf-8") as handle:
            for line in handle:
                line = line.strip()
                if line:
                    records.append(json.loads(line))
    summary = summarize_provenance(records)
    report_path.parent.mkdir(parents=True, exist_ok=True)
    with open(report_path, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, indent=2)
    return summary


def prompt_content_hash(prompt_text: str) -> str:
    """Short hash of prompt body for audit trails."""
    digest = hashlib.sha256(prompt_text.encode("utf-8")).hexdigest()
    return digest[:12]
