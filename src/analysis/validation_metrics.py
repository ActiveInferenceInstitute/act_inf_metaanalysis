"""Metrics for rule-based reference-annotator extraction agreement.

IMPORTANT — this is NOT a human validation study. The "reference" labels are
produced by the deterministic keyword-rule protocols in
``analysis.validation_labeling`` (``apply_primary_rule_protocol`` /
``apply_secondary_rule_protocol``), not by human annotators. The metrics here
therefore measure agreement between the LLM extraction pipeline and an
independent, reproducible rule-based reference — a lower-bound reproducibility
signal, not a gold-standard accuracy. Human gold-standard annotation is future
work (see manuscript conclusion, "Human spot-check coverage").
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
    """Read a primary rule-reference column (``ref_<suffix>``)."""
    return row.get(f"ref_{suffix}", "")


def classify_error(row: dict[str, str]) -> str:
    """Assign an error taxonomy label comparing the pipeline to the rule reference."""
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


def compute_validation_metrics(rows: list[dict[str, str]]) -> dict[str, object]:
    """Compute agreement between the LLM pipeline and the rule-based reference.

    The "reference" labels come from deterministic keyword-rule protocols, NOT
    from human annotators (see the module docstring). Metric keys are named
    accordingly. ``quote_fidelity_rate`` is reported as ``None`` when the
    current corpus stores no verbatim evidence quotes (abstract-only extraction),
    to avoid a spurious ``0.0`` that would read as "0% faithful".
    """
    labeled = [
        r for r in rows if r.get("ref_triage") and r.get("secondary_triage")
    ]
    if not labeled:
        return {
            "sample_size": len(rows),
            "reference_kind": "deterministic_rule_based",
            "status": "pending_labels",
        }

    ref_triage = [_ref_field(r, "triage") for r in labeled]
    secondary_triage = [r.get("secondary_triage", "") for r in labeled]
    pipeline_triage = [r.get("pipeline_triage", "") for r in labeled]

    kappa_interrule = _cohen_kappa(ref_triage, secondary_triage)
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
        "reference_kind": "deterministic_rule_based",
        "kappa_interrule": kappa_interrule,
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


def write_validation_metrics(rows: list[dict[str, str]], output_path: Path) -> dict[str, object]:
    """Compute metrics and persist JSON."""
    metrics = compute_validation_metrics(rows)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(metrics, handle, indent=2)
    return metrics
