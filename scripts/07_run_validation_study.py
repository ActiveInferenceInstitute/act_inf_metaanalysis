#!/usr/bin/env python3
"""Run rule-reference agreement or evaluate an existing human annotation CSV.

Default mode generates deterministic rule references, not human validation.
``--no-auto-labels`` reads ``validation/sample.csv`` without resampling or
modifying it and identifies the supplied reference as human in both reports.
"""

from __future__ import annotations

import argparse
import csv
import logging
import shutil
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project(include_infrastructure=True)

from analysis.validation_labeling import (
    apply_primary_rule_protocol,
    apply_secondary_rule_protocol,
)
from analysis.validation_metrics import classify_error, write_validation_metrics
from analysis.validation_sample import (
    build_stratified_sample,
    load_labels_csv,
    write_sample_csv,
)

logger = logging.getLogger(__name__)


def _apply_rule_reference_labels(sample_path: Path) -> list[dict[str, str]]:
    """Fill an unannotated sample using the two deterministic rule protocols."""
    rows = load_labels_csv(sample_path)
    for row in rows:
        abstract = row.get("abstract_excerpt", "")
        hypothesis_id = row.get("hypothesis_id", "")
        primary = apply_primary_rule_protocol(abstract, hypothesis_id)
        secondary = apply_secondary_rule_protocol(abstract, hypothesis_id)
        row["ref_triage"] = primary.triage
        row["ref_evidence_status"] = primary.evidence_status
        row["ref_evidence_type"] = primary.evidence_type
        row["ref_source_claim"] = primary.source_claim
        row["secondary_triage"] = secondary.triage
        row["secondary_evidence_status"] = secondary.evidence_status
        row["secondary_evidence_type"] = secondary.evidence_type
        row["error_type"] = classify_error(row)
    return rows


def _write_labeled_csv(rows: list[dict[str, str]], path: Path) -> None:
    if not rows:
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main(argv: list[str] | None = None) -> int:
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(description="Validation study orchestrator")
    parser.add_argument("--output-dir", default=str(PROJECT_ROOT / "output"))
    parser.add_argument("--sample-fraction", type=float, default=0.10)
    parser.add_argument("--min-size", type=int, default=200)
    parser.add_argument(
        "--no-auto-labels",
        dest="auto_labels",
        action="store_false",
        default=True,
        help="Skip rule-based reference auto-labeling (use pre-filled human labels).",
    )
    args = parser.parse_args(argv)

    output_dir = Path(args.output_dir)
    data_dir = output_dir / "data"
    validation_dir = output_dir / "validation"
    sample_path = validation_dir / "sample.csv"
    reference_kind = "deterministic_rule_based" if args.auto_labels else "human"
    try:
        if args.auto_labels:
            existing = load_labels_csv(sample_path)
            if any(
                value
                for row in existing
                for key, value in row.items()
                if isinstance(key, str)
                and (key.startswith(("ref_", "secondary_")) or key == "error_type")
            ):
                raise ValueError(
                    f"Refusing to replace annotations in {sample_path}; use --no-auto-labels"
                )
            nanopub_path = data_dir / "nanopublications.jsonl"
            corpus_path = data_dir / "corpus.jsonl"
            if not nanopub_path.exists() or not corpus_path.exists():
                raise ValueError(f"Missing corpus or nanopublications under {data_dir}")
            sample = build_stratified_sample(
                nanopub_path,
                corpus_path,
                fraction=args.sample_fraction,
                min_size=args.min_size,
            )
            write_sample_csv(sample, sample_path)
            labeled = _apply_rule_reference_labels(sample_path)
        else:
            labeled = load_labels_csv(sample_path)

        metrics_path = output_dir / "reports" / "validation_metrics.json"
        metrics = write_validation_metrics(
            labeled, metrics_path, reference_kind=reference_kind
        )
        data_dir.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(metrics_path, data_dir / "validation_metrics.json")
        if args.auto_labels:
            _write_labeled_csv(labeled, validation_dir / "labels_rule_reference.csv")
    except (OSError, ValueError, csv.Error) as exc:
        logger.error("Validation failed: %s", exc)
        return 1
    logger.info("Validation metrics: %s", metrics)
    print(str(metrics_path))

    print(str(sample_path))
    return 0


if __name__ == "__main__":
    sys.exit(main())
