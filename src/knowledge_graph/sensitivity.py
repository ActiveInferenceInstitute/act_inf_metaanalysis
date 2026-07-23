"""Sensitivity analysis across citation-weight policies."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from knowledge_graph.hypothesis import HYPOTHESES, configure_hypotheses
from knowledge_graph.hypothesis_weights import WeightPolicy, score_hypothesis_with_policy
from knowledge_graph.nanopublication import Assertion
from literature.models import Paper


def _rank_scores(scores: dict[str, float]) -> dict[str, int]:
    ordered = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    return {hyp_id: rank + 1 for rank, (hyp_id, _score) in enumerate(ordered)}


def _spearman(rank_a: dict[str, int], rank_b: dict[str, int]) -> float:
    ids = sorted(set(rank_a) & set(rank_b))
    n = len(ids)
    if n < 2:
        return 1.0
    diff_sq = sum((rank_a[i] - rank_b[i]) ** 2 for i in ids)
    return 1.0 - (6 * diff_sq) / (n * (n * n - 1))


def compute_sensitivity_analysis(
    assertions: list[Assertion],
    papers: list[Paper],
    *,
    reference_year: int | None = None,
) -> dict[str, Any]:
    """Score all hypotheses under each weight policy and compare rank stability."""
    paper_years = {p.canonical_id: p.year for p in papers if p.year is not None}
    if reference_year is None and paper_years:
        reference_year = max(paper_years.values())

    default_scores: dict[str, float] = {}
    per_policy: dict[str, dict[str, float]] = {}
    for policy in WeightPolicy:
        scores = {
            h.hypothesis_id: score_hypothesis_with_policy(
                assertions,
                h.hypothesis_id,
                policy,
                paper_years=paper_years,
                reference_year=reference_year,
            )
            for h in HYPOTHESES
        }
        per_policy[policy.value] = scores
        if policy == WeightPolicy.LOG_CITATION:
            default_scores = scores

    default_ranks = _rank_scores(default_scores)
    comparisons: dict[str, Any] = {}
    rank_change_total = 0
    for policy_name, scores in per_policy.items():
        if policy_name == WeightPolicy.LOG_CITATION.value:
            continue
        ranks = _rank_scores(scores)
        spearman = _spearman(default_ranks, ranks)
        # Count hypotheses whose rank position moves relative to the default
        # policy. (A "sign flip" is meaningless here: hypothesis scores are
        # normalized into [0, 1] and can never change sign, so the old
        # sign-flip counter was structurally always zero.)
        rank_changes = sum(
            1 for hyp_id in default_ranks if default_ranks[hyp_id] != ranks.get(hyp_id)
        )
        rank_change_total += rank_changes
        comparisons[policy_name] = {
            "scores": scores,
            "rank_stability_spearman": spearman,
            "rank_change_count": rank_changes,
        }

    return {
        "default_policy": WeightPolicy.LOG_CITATION.value,
        "default_scores": default_scores,
        "policy_comparisons": comparisons,
        "rank_stability_spearman": min(
            (v["rank_stability_spearman"] for v in comparisons.values()),
            default=1.0,
        ),
        "rank_change_count": rank_change_total,
        "reference_year": reference_year,
    }


def write_sensitivity_analysis(
    assertions: list[Assertion],
    papers: list[Paper],
    output_path: Path,
    config_path: Path | None = None,
) -> dict[str, Any]:
    """Compute and persist sensitivity analysis JSON."""
    if config_path:
        configure_hypotheses(config_path)
    result = compute_sensitivity_analysis(assertions, papers)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as handle:
        json.dump(result, handle, indent=2)
    return result
