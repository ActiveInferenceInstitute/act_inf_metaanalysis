"""Stratified sampling for extraction validation studies."""

from __future__ import annotations

import csv
import json
import random
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from knowledge_graph.nanopublication import deserialize_nanopubs
from literature.corpus import Corpus


@dataclass
class ValidationRow:
    """One assertion selected for manual review."""

    assertion_id: str
    paper_id: str
    hypothesis_id: str
    pipeline_triage: str
    source_claim_text: str
    evidence_quote: str
    evidence_status: str
    evidence_type: str
    paper_title: str
    paper_year: str
    abstract_excerpt: str
    stratum: str


def _year_bin(year: int | None) -> str:
    if year is None:
        return "unknown"
    if year < 2015:
        return "2000-2014"
    if year < 2020:
        return "2015-2019"
    return "2020+"


def build_stratified_sample(
    nanopub_path: Path,
    corpus_path: Path,
    *,
    fraction: float = 0.10,
    min_size: int = 200,
    seed: int = 42,
) -> list[ValidationRow]:
    """Sample assertions stratified by hypothesis × triage × year bin."""
    rng = random.Random(seed)
    nanopubs = deserialize_nanopubs(nanopub_path)
    corpus = Corpus.load(corpus_path)
    paper_lookup = {p.canonical_id: p for p in corpus.papers}

    strata: dict[str, list[ValidationRow]] = defaultdict(list)
    for np_obj in nanopubs:
        assertion = np_obj.assertion
        paper = paper_lookup.get(assertion.paper_id)
        year = paper.year if paper else None
        stratum = f"{assertion.hypothesis_id}|{assertion.assertion_type}|{_year_bin(year)}"
        abstract = (paper.abstract or "")[:400] if paper else ""
        title = paper.title if paper else ""
        strata[stratum].append(
            ValidationRow(
                assertion_id=assertion.assertion_id,
                paper_id=assertion.paper_id,
                hypothesis_id=assertion.hypothesis_id,
                pipeline_triage=assertion.assertion_type,
                source_claim_text=assertion.source_claim_text,
                evidence_quote=assertion.evidence_quote,
                evidence_status=assertion.evidence_status,
                evidence_type=assertion.evidence_type,
                paper_title=title,
                paper_year=str(year or ""),
                abstract_excerpt=abstract,
                stratum=stratum,
            )
        )

    target = max(min_size, int(len(nanopubs) * fraction))
    target = min(target, len(nanopubs))
    if not strata:
        return []

    per_stratum = max(1, target // len(strata))
    selected: list[ValidationRow] = []
    for bucket in strata.values():
        rng.shuffle(bucket)
        selected.extend(bucket[:per_stratum])

    if len(selected) < target:
        remaining = [row for bucket in strata.values() for row in bucket if row not in selected]
        rng.shuffle(remaining)
        selected.extend(remaining[: target - len(selected)])

    rng.shuffle(selected)
    return selected[:target]


def write_sample_csv(rows: list[ValidationRow], path: Path) -> None:
    """Write stratified sample for annotation."""
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "assertion_id",
        "paper_id",
        "hypothesis_id",
        "pipeline_triage",
        "source_claim_text",
        "evidence_quote",
        "evidence_status",
        "evidence_type",
        "paper_title",
        "paper_year",
        "abstract_excerpt",
        "stratum",
        "ref_triage",
        "ref_evidence_status",
        "ref_evidence_type",
        "ref_source_claim",
        "secondary_triage",
        "secondary_evidence_status",
        "secondary_evidence_type",
        "error_type",
    ]
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(
                {
                    "assertion_id": row.assertion_id,
                    "paper_id": row.paper_id,
                    "hypothesis_id": row.hypothesis_id,
                    "pipeline_triage": row.pipeline_triage,
                    "source_claim_text": row.source_claim_text,
                    "evidence_quote": row.evidence_quote,
                    "evidence_status": row.evidence_status,
                    "evidence_type": row.evidence_type,
                    "paper_title": row.paper_title,
                    "paper_year": row.paper_year,
                    "abstract_excerpt": row.abstract_excerpt,
                    "stratum": row.stratum,
                    "ref_triage": "",
                    "ref_evidence_status": "",
                    "ref_evidence_type": "",
                    "ref_source_claim": "",
                    "secondary_triage": "",
                    "secondary_evidence_status": "",
                    "secondary_evidence_type": "",
                    "error_type": "",
                }
            )


def load_labels_csv(path: Path) -> list[dict[str, str]]:
    """Load annotation CSV rows."""
    if not path.exists():
        return []
    with open(path, encoding="utf-8") as handle:
        return list(csv.DictReader(handle))
