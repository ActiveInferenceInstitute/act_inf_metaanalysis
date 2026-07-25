"""Deterministic preparation of full-text and human-review pilot queues."""

from __future__ import annotations

import csv
import hashlib
import json
from pathlib import Path
from typing import Any

from literature.corpus import Corpus

PILOT_SCHEMA_VERSION = "1.0"


def _rank(canonical_id: str, seed: int) -> str:
    return hashlib.sha256(f"{seed}:{canonical_id}".encode()).hexdigest()


def _write_csv(path: Path, rows: list[dict[str, str]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def prepare_pilot_queues(
    output_dir: Path,
    *,
    fulltext_size: int = 100,
    human_size: int = 200,
    seed: int = 42,
) -> dict[str, Any]:
    """Write reproducible queues and protocols without fabricating labels."""
    data_dir = output_dir / "data"
    validation_dir = output_dir / "validation"
    corpus_path = data_dir / "corpus.jsonl"
    if not corpus_path.exists():
        raise FileNotFoundError(corpus_path)
    papers = Corpus.load(corpus_path).papers
    ranked = sorted(papers, key=lambda paper: _rank(paper.canonical_id, seed))
    fulltext_candidates = [paper for paper in ranked if paper.pdf_url or paper.arxiv_id]
    fulltext_rows = [
        {
            "paper_id": paper.canonical_id,
            "title": paper.title,
            "year": str(paper.year or ""),
            "pdf_url": paper.pdf_url or "",
            "full_text_source": paper.full_text_source or ("arxiv" if paper.arxiv_id else ""),
            "abstract_excerpt": (paper.abstract or "")[:500],
            "review_status": "unreviewed",
            "source_section": "",
            "page_or_location": "",
            "evidence_quote": "",
            "human_stance": "",
            "human_evidence_type": "",
            "notes": "",
        }
        for paper in fulltext_candidates[: max(0, fulltext_size)]
    ]
    fulltext_fields = list(fulltext_rows[0]) if fulltext_rows else [
        "paper_id", "title", "year", "pdf_url", "full_text_source", "abstract_excerpt",
        "review_status", "source_section", "page_or_location", "evidence_quote",
        "human_stance", "human_evidence_type", "notes",
    ]
    fulltext_path = validation_dir / "fulltext_pilot_queue.csv"
    _write_csv(fulltext_path, fulltext_rows, fulltext_fields)

    sample_path = validation_dir / "sample.csv"
    human_rows: list[dict[str, str]] = []
    if sample_path.exists():
        with sample_path.open(encoding="utf-8") as handle:
            sampled = list(csv.DictReader(handle))
        sampled.sort(key=lambda row: _rank(row.get("assertion_id", ""), seed))
        for row in sampled[: max(0, human_size)]:
            human_rows.append({
                **row,
                "human_stance": "",
                "human_evidence_status": "",
                "human_evidence_type": "",
                "human_source_claim": "",
                "human_evidence_quote": "",
                "adjudication_status": "unreviewed",
                "annotator_notes": "",
            })
    human_fields = list(human_rows[0]) if human_rows else [
        "assertion_id", "paper_id", "hypothesis_id", "pipeline_triage", "human_stance",
        "human_evidence_status", "human_evidence_type", "human_source_claim",
        "human_evidence_quote", "adjudication_status", "annotator_notes",
    ]
    human_path = validation_dir / "human_calibration_queue.csv"
    _write_csv(human_path, human_rows, human_fields)

    (validation_dir / "fulltext_pilot_protocol.md").write_text(
        "# Full-text evidence pilot protocol\n\n"
        f"Schema version: `{PILOT_SCHEMA_VERSION}`; deterministic seed: `{seed}`.\n\n"
        "Select only the queued open-full-text records. Record the exact source "
        "section and page/location for each hypothesis-relevant quote. This pilot "
        "does not modify the primary abstract-only nanopublications or scores. "
        "Record access failures and ambiguous passages rather than inferring them.\n",
        encoding="utf-8",
    )
    (validation_dir / "human_calibration_protocol.md").write_text(
        "# Human calibration protocol\n\n"
        f"Schema version: `{PILOT_SCHEMA_VERSION}`; deterministic queue seed: `{seed}`.\n\n"
        "Annotators independently label stance (`supports`, `contradicts`, `neutral`), "
        "evidence status, evidence type, source claim, and verbatim evidence quote "
        "from the supplied abstract. Do not use the pipeline label as a cue. Adjudicate "
        "disagreements before computing agreement, precision, recall, F1, quote fidelity, "
        "and uncertainty. Empty queues mean human annotation has not yet been supplied.\n",
        encoding="utf-8",
    )
    manifest = {
        "schema_version": PILOT_SCHEMA_VERSION,
        "seed": seed,
        "fulltext_candidates": len(fulltext_candidates),
        "fulltext_queue_rows": len(fulltext_rows),
        "human_queue_rows": len(human_rows),
        "human_labels_present": False,
        "primary_analysis_unchanged": True,
        "files": {
            "fulltext_queue": str(fulltext_path.relative_to(output_dir)),
            "human_queue": str(human_path.relative_to(output_dir)),
        },
    }
    manifest_path = validation_dir / "pilot_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    return manifest


__all__ = ["PILOT_SCHEMA_VERSION", "prepare_pilot_queues"]
