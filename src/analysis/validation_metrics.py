"""Agreement metrics for explicitly identified rule or human reference labels.

Rule references measure reproducibility, not human accuracy. Human mode consumes
the supplied primary annotations; a second annotator is optional and is never
reported as an inter-rule comparison.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Iterable

VALID_TRIAGE = {"supports", "contradicts", "neutral", "irrelevant"}
VALID_EVIDENCE_STATUS = {"explicit_claim", "mentions", "no_evidence"}
VALID_EVIDENCE_TYPE = {"theoretical", "empirical", "none"}


def _cohen_kappa(labels_a: list[str], labels_b: list[str]) -> float:
    if len(labels_a) != len(labels_b) or not labels_a:
        return 0.0
    categories = sorted(set(labels_a) | set(labels_b))
    n = len(labels_a)
    agree = sum(1 for a, b in zip(labels_a, labels_b) if a == b)
    p_o = agree / n
    p_e = 0.0
    for cat in categories:
        p_a = labels_a.count(cat) / n
        p_b = labels_b.count(cat) / n
        p_e += p_a * p_b
    if p_e >= 1.0:
        return 1.0
    return (p_o - p_e) / (1.0 - p_e)


def _precision_recall_f1(
    gold: Iterable[str],
    predicted: Iterable[str],
    positive: str,
) -> tuple[float, float, float]:
    gold_list = list(gold)
    pred_list = list(predicted)
    tp = sum(1 for g, p in zip(gold_list, pred_list) if g == positive and p == positive)
    fp = sum(1 for g, p in zip(gold_list, pred_list) if g != positive and p == positive)
    fn = sum(1 for g, p in zip(gold_list, pred_list) if g == positive and p != positive)
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (
        2 * precision * recall / (precision + recall)
        if (precision + recall)
        else 0.0
    )
    return precision, recall, f1


def _ref_field(row: dict[str, str], suffix: str) -> str:
    """Read a primary reference column (``ref_<suffix>``)."""
    return row.get(f"ref_{suffix}", "")


def classify_error(row: dict[str, str]) -> str:
    """Assign an error taxonomy label comparing the pipeline to its reference."""
    reference = _ref_field(row, "triage")
    pipeline = row.get("pipeline_triage", "")
    quote = row.get("evidence_quote", "")
    abstract = row.get("abstract_excerpt", "")

    if reference == "irrelevant" and pipeline != "irrelevant":
        return "over_extraction"
    if reference != pipeline and reference in {"supports", "contradicts"} and pipeline in {"supports", "contradicts"}:
        return "direction_inversion"
    if quote and quote not in abstract:
        return "quote_mismatch"
    if reference != pipeline:
        return "triage_mismatch"
    if _ref_field(row, "evidence_status") != row.get("evidence_status"):
        return "evidence_status_error"
    if _ref_field(row, "evidence_type") != row.get("evidence_type"):
        return "evidence_type_error"
    return "none"


def compute_validation_metrics(
    rows: list[dict[str, str]],
    *,
    reference_kind: str = "deterministic_rule_based",
) -> dict[str, object]:
    """Compute agreement without silently discarding incomplete annotations."""
    if reference_kind not in {"deterministic_rule_based", "human"}:
        raise ValueError(f"Unknown reference kind: {reference_kind}")
    if not rows:
        return {
            "sample_size": 0,
            "reference_kind": reference_kind,
            "status": "pending_labels",
        }
    required = {
        "ref_triage": VALID_TRIAGE,
        "pipeline_triage": VALID_TRIAGE,
        "ref_evidence_status": VALID_EVIDENCE_STATUS,
        "ref_evidence_type": VALID_EVIDENCE_TYPE,
    }
    for index, row in enumerate(rows, 1):
        for field, allowed in required.items():
            if row.get(field) not in allowed:
                raise ValueError(f"Annotation row {index} has missing or invalid {field}")
        secondary = row.get("secondary_triage")
        if (secondary or reference_kind == "deterministic_rule_based") and secondary not in VALID_TRIAGE:
            raise ValueError(f"Annotation row {index} has missing or invalid secondary_triage")

    labeled = rows
    ref_triage = [_ref_field(r, "triage") for r in labeled]
    pipeline_triage = [r["pipeline_triage"] for r in labeled]
    paired = [r for r in labeled if r.get("secondary_triage")]
    secondary_kappa = (
        _cohen_kappa(
            [r["ref_triage"] for r in paired],
            [r["secondary_triage"] for r in paired],
        )
        if paired else None
    )
    kappa_reference_pipeline = _cohen_kappa(ref_triage, pipeline_triage)
    precision, recall, f1 = _precision_recall_f1(
        ref_triage, pipeline_triage, positive="supports"
    )

    error_counts: Counter[str] = Counter()
    for row in labeled:
        error_counts[classify_error(row)] += 1
    total = len(labeled)
    taxonomy_rates = {
        key: count / total for key, count in error_counts.items() if key != "none"
    }

    confusion: dict[str, dict[str, int]] = {}
    for gold, pred in zip(ref_triage, pipeline_triage):
        confusion.setdefault(gold, {})
        confusion[gold][pred] = confusion[gold].get(pred, 0) + 1

    quote_rows = [r for r in labeled if r.get("evidence_quote")]
    if quote_rows:
        quote_matches = sum(
            1
            for row in quote_rows
            if row.get("evidence_quote", "") in row.get("abstract_excerpt", "")
        )
        quote_fidelity: float | None = quote_matches / len(quote_rows)
        quote_status = "measured"
    else:
        quote_fidelity = None
        quote_status = "not_applicable_no_evidence_quotes"

    return {
        "sample_size": total,
        "reference_kind": reference_kind,
        "kappa_interrule": secondary_kappa if reference_kind == "deterministic_rule_based" else None,
        "kappa_interannotator": secondary_kappa if reference_kind == "human" else None,
        "secondary_sample_size": len(paired),
        "kappa_reference_pipeline": kappa_reference_pipeline,
        "precision": precision,
        "recall": recall,
        "f1": f1,
        "quote_fidelity_rate": quote_fidelity,
        "quote_fidelity_status": quote_status,
        "error_taxonomy_rates": taxonomy_rates,
        "confusion_reference_vs_pipeline": confusion,
        "status": "complete",
    }


def write_validation_metrics(
    rows: list[dict[str, str]],
    output_path: Path,
    *,
    reference_kind: str = "deterministic_rule_based",
) -> dict[str, object]:
    """Persist only complete metrics for the explicitly selected reference."""
    metrics = compute_validation_metrics(rows, reference_kind=reference_kind)
    if metrics["status"] != "complete":
        raise ValueError("No usable reference annotations")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    return metrics
