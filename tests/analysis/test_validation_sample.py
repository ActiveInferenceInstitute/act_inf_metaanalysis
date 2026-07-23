"""Tests for analysis.validation_sample (stratified sampling for the rule-based
reference-annotator agreement study; see analysis.validation_labeling for why
these are NOT human annotations)."""

from __future__ import annotations

from pathlib import Path

from analysis.validation_sample import (
    ValidationRow,
    _year_bin,
    build_stratified_sample,
    load_labels_csv,
    write_sample_csv,
)
from knowledge_graph.nanopublication import Assertion, create_nanopub, serialize_nanopubs
from literature.corpus import Corpus
from literature.models import Paper


def _make_corpus_and_nanopubs(tmp_path: Path) -> tuple[Path, Path]:
    papers = [
        Paper(title="Old FEP paper", abstract="We show the free energy principle is universal.", year=2010, doi="10.1/a"),
        Paper(title="Recent AIF paper", abstract="Active inference optimal decision-making experiment.", year=2022, doi="10.1/b"),
        Paper(title="No-year paper", abstract="Markov blanket boundary discussion.", year=None, doi="10.1/c"),
    ]
    corpus = Corpus(papers)
    corpus_path = tmp_path / "corpus.jsonl"
    corpus.save(corpus_path)

    nanopubs = [
        create_nanopub(
            Assertion(
                assertion_id="a1",
                paper_id=papers[0].canonical_id,
                claim="reasoning",
                assertion_type="supports",
                hypothesis_id="FEP_UNIVERSALITY",
                source_claim_text="claim text",
                evidence_quote="quote",
                evidence_status="explicit_claim",
                evidence_type="theoretical",
            )
        ),
        create_nanopub(
            Assertion(
                assertion_id="a2",
                paper_id=papers[1].canonical_id,
                claim="reasoning",
                assertion_type="contradicts",
                hypothesis_id="AIF_OPTIMALITY",
                source_claim_text="claim text 2",
                evidence_quote="",
                evidence_status="mentions",
                evidence_type="empirical",
            )
        ),
        create_nanopub(
            Assertion(
                assertion_id="a3",
                paper_id=papers[2].canonical_id,
                claim="reasoning",
                assertion_type="neutral",
                hypothesis_id="MARKOV_BLANKET_REALISM",
            )
        ),
    ]
    nanopub_path = tmp_path / "nanopublications.jsonl"
    serialize_nanopubs(nanopubs, nanopub_path)
    return nanopub_path, corpus_path


def test_year_bin_boundaries():
    assert _year_bin(None) == "unknown"
    assert _year_bin(2010) == "2000-2014"
    assert _year_bin(2017) == "2015-2019"
    assert _year_bin(2023) == "2020+"


def test_build_stratified_sample_covers_every_stratum(tmp_path: Path):
    nanopub_path, corpus_path = _make_corpus_and_nanopubs(tmp_path)
    sample = build_stratified_sample(nanopub_path, corpus_path, fraction=1.0, min_size=1)

    assert len(sample) == 3
    strata = {row.stratum for row in sample}
    assert len(strata) == 3
    assert all(isinstance(row, ValidationRow) for row in sample)
    row_by_assertion = {row.assertion_id: row for row in sample}
    assert row_by_assertion["a1"].paper_year == "2010"
    assert row_by_assertion["a3"].paper_year == ""


def test_build_stratified_sample_is_deterministic_for_fixed_seed(tmp_path: Path):
    nanopub_path, corpus_path = _make_corpus_and_nanopubs(tmp_path)
    first = build_stratified_sample(nanopub_path, corpus_path, fraction=1.0, min_size=1, seed=7)
    second = build_stratified_sample(nanopub_path, corpus_path, fraction=1.0, min_size=1, seed=7)
    assert [row.assertion_id for row in first] == [row.assertion_id for row in second]


def test_build_stratified_sample_empty_nanopubs_returns_empty(tmp_path: Path):
    empty_nanopub_path = tmp_path / "empty.jsonl"
    empty_nanopub_path.write_text("")
    _, corpus_path = _make_corpus_and_nanopubs(tmp_path)
    assert build_stratified_sample(empty_nanopub_path, corpus_path) == []


def test_write_sample_csv_and_load_labels_csv_roundtrip(tmp_path: Path):
    nanopub_path, corpus_path = _make_corpus_and_nanopubs(tmp_path)
    sample = build_stratified_sample(nanopub_path, corpus_path, fraction=1.0, min_size=1)

    csv_path = tmp_path / "validation" / "sample.csv"
    write_sample_csv(sample, csv_path)
    assert csv_path.exists()

    rows = load_labels_csv(csv_path)
    assert len(rows) == 3
    assert {row["assertion_id"] for row in rows} == {"a1", "a2", "a3"}
    # Reference/secondary columns are pre-populated empty, ready for a rule
    # protocol (or a genuine human annotator) to fill in later.
    assert all(row["ref_triage"] == "" for row in rows)


def test_load_labels_csv_missing_file_returns_empty(tmp_path: Path):
    assert load_labels_csv(tmp_path / "does_not_exist.csv") == []
