"""Citation-weight policies for hypothesis scoring sensitivity analysis."""

from __future__ import annotations

import enum
import math
from statistics import median
from typing import Callable

from knowledge_graph.nanopublication import Assertion


class WeightPolicy(enum.Enum):
    """Supported assertion weighting policies."""

    LOG_CITATION = "log_citation"
    UNIFORM = "uniform"
    CONFIDENCE_ONLY = "confidence_only"
    RAW_CITATION = "raw_citation"
    AGE_DISCOUNT = "age_discount"
    FIELD_NORMALIZED = "field_normalized"


def _log_citation_weight(citation_count: int, confidence: float, **_ctx: object) -> float:
    return math.log(1 + max(0, citation_count)) * confidence


def _uniform_weight(_citation_count: int, _confidence: float, **_ctx: object) -> float:
    return 1.0


def _confidence_only_weight(_citation_count: int, confidence: float, **_ctx: object) -> float:
    return confidence


def _raw_citation_weight(citation_count: int, confidence: float, **_ctx: object) -> float:
    return max(0, citation_count) * confidence


def _age_discount_weight(
    citation_count: int,
    confidence: float,
    *,
    paper_year: int | None = None,
    reference_year: int | None = None,
    **_ctx: object,
) -> float:
    base = math.log(1 + max(0, citation_count)) * confidence
    if paper_year is None or reference_year is None:
        return base
    age = max(0, reference_year - paper_year)
    decay = 1.0 / (1.0 + 0.05 * age)
    return base * decay


def _field_normalized_weight(
    citation_count: int,
    confidence: float,
    *,
    cohort_median_citations: float | None = None,
    **_ctx: object,
) -> float:
    cites = max(0, citation_count)
    if cohort_median_citations and cohort_median_citations > 0:
        normalized = cites / cohort_median_citations
    else:
        normalized = cites
    return math.log(1 + normalized) * confidence


_POLICY_FN: dict[WeightPolicy, Callable[..., float]] = {
    WeightPolicy.LOG_CITATION: _log_citation_weight,
    WeightPolicy.UNIFORM: _uniform_weight,
    WeightPolicy.CONFIDENCE_ONLY: _confidence_only_weight,
    WeightPolicy.RAW_CITATION: _raw_citation_weight,
    WeightPolicy.AGE_DISCOUNT: _age_discount_weight,
    WeightPolicy.FIELD_NORMALIZED: _field_normalized_weight,
}


def assertion_weight(
    assertion: Assertion,
    policy: WeightPolicy = WeightPolicy.LOG_CITATION,
    *,
    paper_year: int | None = None,
    reference_year: int | None = None,
    cohort_median_citations: float | None = None,
) -> float:
    """Compute a single assertion weight under *policy*."""
    fn = _POLICY_FN[policy]
    return fn(
        assertion.citation_count,
        assertion.confidence,
        paper_year=paper_year,
        reference_year=reference_year,
        cohort_median_citations=cohort_median_citations,
    )


def cohort_median_citations(
    assertions: list[Assertion],
    paper_years: dict[str, int],
    target_year: int | None = None,
) -> float:
    """Median citation count for assertions in the same publication year cohort."""
    cites: list[int] = []
    for assertion in assertions:
        year = paper_years.get(assertion.paper_id)
        if year is None:
            continue
        if target_year is not None and year != target_year:
            continue
        cites.append(max(0, assertion.citation_count))
    if not cites:
        return 0.0
    return float(median(cites))


def score_hypothesis_with_policy(
    assertions: list[Assertion],
    hypothesis_id: str,
    policy: WeightPolicy = WeightPolicy.LOG_CITATION,
    *,
    paper_years: dict[str, int] | None = None,
    reference_year: int | None = None,
) -> float:
    """Citation-weighted score for one hypothesis under *policy*."""
    relevant = [a for a in assertions if a.hypothesis_id == hypothesis_id]
    if not relevant:
        return 0.0

    paper_years = paper_years or {}
    support_sum = 0.0
    contradict_sum = 0.0
    total_sum = 0.0

    for assertion in relevant:
        cohort_med = None
        if policy == WeightPolicy.FIELD_NORMALIZED:
            year = paper_years.get(assertion.paper_id)
            cohort_med = cohort_median_citations(relevant, paper_years, target_year=year)
        weight = assertion_weight(
            assertion,
            policy,
            paper_year=paper_years.get(assertion.paper_id),
            reference_year=reference_year,
            cohort_median_citations=cohort_med,
        )
        total_sum += weight
        if assertion.assertion_type == "supports":
            support_sum += weight
        elif assertion.assertion_type == "contradicts":
            contradict_sum += weight

    if total_sum == 0.0:
        return 0.0
    return (support_sum - contradict_sum) / total_sum
