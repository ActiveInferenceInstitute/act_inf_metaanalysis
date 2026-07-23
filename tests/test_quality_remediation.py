"""Tests for quality remediation modules (corpus invariant, weights, validation)."""

from __future__ import annotations

from pathlib import Path

import pytest

from analysis.validation_labeling import (
    apply_primary_rule_protocol,
    apply_secondary_rule_protocol,
)
from analysis.validation_metrics import compute_validation_metrics
from knowledge_graph.hypothesis_weights import WeightPolicy, score_hypothesis_with_policy
from knowledge_graph.nanopublication import Assertion
from knowledge_graph.provenance import ExtractionProvenance, summarize_provenance
from literature.corpus import Corpus
from literature.models import Paper
from manuscript.variables import compute_variables


def test_drop_before_year_mutates_corpus():
    corpus = Corpus(
        [
            Paper(title="old", year=1977, doi="10.1/old"),
            Paper(title="ok", year=2010, doi="10.1/ok"),
        ]
    )
    removed = corpus.drop_before_year(2000)
    assert removed == 1
    assert len(corpus) == 1
    assert corpus.papers[0].year == 2010


def test_corpus_load_applies_min_year(tmp_path: Path):
    corpus = Corpus(
        [
            Paper(title="old", year=1977, doi="10.1/old"),
            Paper(title="ok", year=2010, doi="10.1/ok"),
        ]
    )
    path = tmp_path / "corpus.jsonl"
    corpus.save(path)
    loaded = Corpus.load(path, min_year=2000)
    assert len(loaded) == 1


def test_weight_policies_differ():
    assertions = [
        Assertion(
            assertion_id="a1",
            paper_id="p1",
            claim="c",
            assertion_type="supports",
            hypothesis_id="FEP_UNIVERSALITY",
            confidence=1.0,
            citation_count=100,
        ),
        Assertion(
            assertion_id="a2",
            paper_id="p2",
            claim="c",
            assertion_type="contradicts",
            hypothesis_id="FEP_UNIVERSALITY",
            confidence=1.0,
            citation_count=1,
        ),
    ]
    log_score = score_hypothesis_with_policy(
        assertions, "FEP_UNIVERSALITY", WeightPolicy.LOG_CITATION
    )
    uniform_score = score_hypothesis_with_policy(
        assertions, "FEP_UNIVERSALITY", WeightPolicy.UNIFORM
    )
    assert log_score != uniform_score


def test_parse_confidence_robust_to_words_and_percents():
    """A word/percent/garbage confidence must never crash extraction."""
    from knowledge_graph.llm_extraction import _parse_confidence

    assert _parse_confidence("high") == 0.8
    assert _parse_confidence("HIGH") == 0.8
    assert _parse_confidence("very high") == 0.9
    assert _parse_confidence(0.7) == 0.7
    assert _parse_confidence("0.7") == 0.7
    assert _parse_confidence("80%") == 0.8
    assert _parse_confidence(85) == 1.0  # bare out-of-range number clamps
    assert _parse_confidence(1.5) == 1.0
    assert _parse_confidence(-0.3) == 0.0
    assert _parse_confidence("garbage") == 0.5
    assert _parse_confidence("") == 0.5
    assert 0.0 <= _parse_confidence("anything") <= 1.0


def test_rule_protocols_produce_labels():
    """The reference protocols are deterministic keyword rules, not humans."""
    abstract = "We show that the free energy principle is universal and self-organizing."
    primary = apply_primary_rule_protocol(abstract, "FEP_UNIVERSALITY")
    secondary = apply_secondary_rule_protocol(abstract, "FEP_UNIVERSALITY")
    assert primary.triage in {"supports", "contradicts", "neutral", "irrelevant"}
    assert secondary.triage in {"supports", "contradicts", "neutral", "irrelevant"}
    # Determinism: identical input yields identical labels.
    assert apply_primary_rule_protocol(abstract, "FEP_UNIVERSALITY").triage == primary.triage


def test_validation_metrics_on_labeled_rows():
    rows = [
        {
            "ref_triage": "supports",
            "secondary_triage": "supports",
            "pipeline_triage": "supports",
            "evidence_quote": "free energy",
            "abstract_excerpt": "This paper discusses free energy.",
            "evidence_status": "mentions",
            "evidence_type": "theoretical",
            "ref_evidence_status": "mentions",
            "ref_evidence_type": "theoretical",
        },
        {
            "ref_triage": "irrelevant",
            "secondary_triage": "neutral",
            "pipeline_triage": "supports",
            "evidence_quote": "",
            "abstract_excerpt": "Unrelated topic.",
            "evidence_status": "mentions",
            "evidence_type": "none",
            "ref_evidence_status": "no_evidence",
            "ref_evidence_type": "none",
        },
    ]
    metrics = compute_validation_metrics(rows)
    assert metrics["sample_size"] == 2
    assert metrics["reference_kind"] == "deterministic_rule_based"
    assert "kappa_interrule" in metrics
    assert "kappa_reference_pipeline" in metrics
    # Row 1 has a verbatim quote present in its abstract → fidelity measured.
    assert metrics["quote_fidelity_rate"] == 1.0
    assert metrics["quote_fidelity_status"] == "measured"


def test_validation_metrics_quote_fidelity_na_when_no_quotes():
    """Zero stored quotes → N/A, not a misleading 0.0 fidelity rate."""
    rows = [
        {
            "ref_triage": "supports",
            "secondary_triage": "neutral",
            "pipeline_triage": "supports",
            "evidence_quote": "",
            "abstract_excerpt": "Some abstract text.",
            "evidence_status": "mentions",
            "evidence_type": "theoretical",
            "ref_evidence_status": "mentions",
            "ref_evidence_type": "theoretical",
        }
    ]
    metrics = compute_validation_metrics(rows)
    assert metrics["quote_fidelity_rate"] is None
    assert metrics["quote_fidelity_status"] == "not_applicable_no_evidence_quotes"


def test_provenance_summary():
    record = {
        "provenance": ExtractionProvenance.create(
            paper_id="doi:10.1/x",
            source_passage="abstract text",
            model_id="gemma3:4b",
            llm_url="http://localhost:11434",
            pipeline_version="2.0.1",
            run_id="abc",
        ).to_dict()
    }
    summary = summarize_provenance([record])
    assert summary["total"] == 1


def test_corpus_size_alignment_when_output_present() -> None:
    """Regression: filtered corpus N matches citation nodes after QC."""
    root = Path(__file__).resolve().parents[1]
    corpus_path = root / "output" / "data" / "corpus.jsonl"
    if not corpus_path.exists():
        pytest.skip("pipeline output not present")
    variables = compute_variables(root / "output", project_root=root)
    assert variables["CORPUS_SIZE"] == variables["CITATION_NODES"]
    loaded = Corpus.load(corpus_path, min_year=2000)
    assert str(len(loaded)) == variables["CORPUS_SIZE"]
    years = [p.year for p in loaded.papers if p.year is not None]
    if years:
        assert min(years) >= int(variables["INCLUSION_YEAR_START"])


def test_compute_variables_inclusion_period(tmp_path: Path):
    manuscript = tmp_path / "manuscript"
    manuscript.mkdir()
    (manuscript / "config.yaml").write_text(
        "project_config:\n  search:\n    start_year: 2000\n"
    )
    data = tmp_path / "data"
    data.mkdir()
    (data / "corpus.jsonl").write_text(
        '{"title":"t","year":2010,"doi":"10.1/a"}\n'
        '{"title":"t2","year":2020,"doi":"10.1/b"}\n'
    )
    (data / "temporal_analysis.json").write_text(
        '{"first_year":2010,"last_year":2020,"year_counts":{"2010":1,"2020":1},"cagr":0.1,"doubling_time":2.0,"peak_year":2020}'
    )
    (data / "citation_network.json").write_text(
        '{"num_edges":1,"num_nodes":2,"connected_components":1,"density":0.01,"avg_in_degree":0.5}'
    )
    (data / "subfield_classification.json").write_text('{"A1_formal":1,"A2_philosophy":1}')
    vars_ = compute_variables(tmp_path, project_root=tmp_path)
    assert vars_["CORPUS_SIZE"] == "2"
    assert vars_["CITATION_NODES"] == "2"
    assert vars_["INCLUSION_YEAR_START"] == "2000"
    assert vars_["INCLUSION_PERIOD"] == "2000–2020"
