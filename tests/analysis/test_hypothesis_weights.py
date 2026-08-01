"""Tests for citation-weight policies (hypothesis_weights.py).

MED-17: the non-default weighting policies that feed `hypothesis_sensitivity.json`
previously had no direct unit tests. These pin their semantics so a defect in the
age-discount decay or field-normalization is caught, not silent.
"""

from __future__ import annotations

from knowledge_graph.hypothesis_weights import (
    WeightPolicy,
    assertion_weight,
    cohort_median_citations,
    score_hypothesis_with_policy,
)
from knowledge_graph.nanopublication import Assertion


def _assertion(*, type_: str = "supports", cites: int = 10, conf: float = 0.8,
               paper: str = "p1", hyp: str = "H1") -> Assertion:
    return Assertion(
        assertion_id=f"llm_{paper}_{hyp}",
        paper_id=paper,
        claim="claim",
        assertion_type=type_,
        hypothesis_id=hyp,
        confidence=conf,
        citation_count=cites,
    )


def test_log_citation_grows_with_citations():
    low = assertion_weight(_assertion(cites=1, conf=1.0), WeightPolicy.LOG_CITATION)
    high = assertion_weight(_assertion(cites=100, conf=1.0), WeightPolicy.LOG_CITATION)
    assert low < high
    # log(1+0) = 0 for zero-citation assertions
    assert assertion_weight(_assertion(cites=0, conf=1.0), WeightPolicy.LOG_CITATION) == 0.0


def test_raw_citation_linear_vs_log_dampening():
    raw = assertion_weight(_assertion(cites=10 ** 6, conf=1.0), WeightPolicy.RAW_CITATION)
    log = assertion_weight(_assertion(cites=10 ** 6, conf=1.0), WeightPolicy.LOG_CITATION)
    assert raw > log  # raw weighs hyper-cited papers far more


def test_confidence_only_ignores_citations():
    same_conf = assertion_weight(_assertion(cites=7, conf=0.8), WeightPolicy.CONFIDENCE_ONLY)
    diff_cites = assertion_weight(_assertion(cites=7000, conf=0.8), WeightPolicy.CONFIDENCE_ONLY)
    assert same_conf == diff_cites == 0.8


def test_age_discount_decays_with_age():
    recent = assertion_weight(
        _assertion(cites=50, conf=1.0), WeightPolicy.AGE_DISCOUNT, paper_year=2020, reference_year=2024
    )
    old = assertion_weight(
        _assertion(cites=50, conf=1.0), WeightPolicy.AGE_DISCOUNT, paper_year=2000, reference_year=2024
    )
    assert old < recent  # 24-year-old paper is discounted more than a 4-year-old one
    # No year context -> no discount (base weight returned)
    base = assertion_weight(_assertion(cites=50, conf=1.0), WeightPolicy.AGE_DISCOUNT)
    assert base == assertion_weight(_assertion(cites=50, conf=1.0), WeightPolicy.LOG_CITATION)


def test_field_normalized_uses_cohort_median():
    # Cohort median 10 -> a 10-citation assertion normalizes to ratio 1
    w_median = assertion_weight(
        _assertion(cites=10, conf=1.0), WeightPolicy.FIELD_NORMALIZED, cohort_median_citations=10.0
    )
    # No cohort -> raw citations used (no normalization)
    w_none = assertion_weight(_assertion(cites=10, conf=1.0), WeightPolicy.FIELD_NORMALIZED)
    assert w_median != w_none


def test_cohort_median_citations_ignores_other_years():
    assertions = [
        _assertion(cites=4, paper="p1"),
        _assertion(cites=8, paper="p2"),
        _assertion(cites=100, paper="p3"),
    ]
    years = {"p1": 2020, "p2": 2020, "p3": 2021}
    assert cohort_median_citations(assertions, years, target_year=2020) == 6.0  # median(4,8)
    assert cohort_median_citations(assertions, years, target_year=2021) == 100.0
    assert cohort_median_citations(assertions, years) == 8.0  # median(4,8,100)


def test_uniform_policy_scores_direction_balance():
    """Under uniform weights the score is the share of supports minus contradicts."""
    score = score_hypothesis_with_policy(
        [
            _assertion(type_="supports", hyp="H1"),
            _assertion(type_="supports", hyp="H1"),
            _assertion(type_="contradicts", hyp="H1"),
            _assertion(type_="neutral", hyp="H1"),
        ],
        "H1",
        policy=WeightPolicy.UNIFORM,
    )
    assert abs(score - ((2 - 1) / 4)) < 1e-9
