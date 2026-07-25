"""Tests for src/manuscript/variables.py — compute_variables and inject_variables.

Tests cover:
- _latex_number formatting (thousand separators)
- _count_jsonl_lines counting
- _count_total_references from corpus JSONL
- compute_variables with full / partial / empty pipeline output
- inject_variables placeholder replacement
- Edge cases: missing files, empty JSON, malformed data
"""

from __future__ import annotations

import json
import sys
from pathlib import Path


# Ensure infrastructure is importable
REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

from manuscript.variables import (
    _latex_number,
    _count_jsonl_lines,
    _count_total_references,
    _load_json,
    collect_manuscript_tokens,
    compute_variables,
    inject_variables,
    write_manuscript_variables,
)


# ── _latex_number ────────────────────────────────────────────────────────


class TestLatexNumber:
    """Test LaTeX thousand separator formatting."""

    def test_small_number(self):
        assert _latex_number(42) == "42"

    def test_three_digits(self):
        assert _latex_number(775) == "775"

    def test_four_digits(self):
        assert _latex_number(1834) == "1,834"

    def test_five_digits(self):
        assert _latex_number(28073) == "28,073"

    def test_six_digits(self):
        assert _latex_number(123456) == "123,456"

    def test_seven_digits(self):
        assert _latex_number(1234567) == "1,234,567"

    def test_zero(self):
        assert _latex_number(0) == "0"

    def test_one(self):
        assert _latex_number(1) == "1"

    def test_exactly_1000(self):
        assert _latex_number(1000) == "1,000"


# ── _count_jsonl_lines ──────────────────────────────────────────────────


class TestCountJsonlLines:
    """Test JSONL line counter."""

    def test_nonexistent_file(self, tmp_path):
        assert _count_jsonl_lines(tmp_path / "missing.jsonl") == 0

    def test_empty_file(self, tmp_path):
        p = tmp_path / "empty.jsonl"
        p.write_text("")
        assert _count_jsonl_lines(p) == 0

    def test_three_lines(self, tmp_path):
        p = tmp_path / "data.jsonl"
        p.write_text('{"a":1}\n{"b":2}\n{"c":3}\n')
        assert _count_jsonl_lines(p) == 3

    def test_blank_lines_skipped(self, tmp_path):
        p = tmp_path / "data.jsonl"
        p.write_text('{"a":1}\n\n{"b":2}\n\n')
        assert _count_jsonl_lines(p) == 2


# ── _count_total_references ─────────────────────────────────────────────


class TestCountTotalReferences:
    """Test total references counter across corpus JSONL."""

    def test_nonexistent_file(self, tmp_path):
        assert _count_total_references(tmp_path / "nope.jsonl") == 0

    def test_papers_with_references(self, tmp_path):
        p = tmp_path / "corpus.jsonl"
        lines = [
            json.dumps({"title": "A", "references": ["r1", "r2", "r3"]}),
            json.dumps({"title": "B", "references": ["r4"]}),
            json.dumps({"title": "C", "references": []}),
        ]
        p.write_text("\n".join(lines) + "\n")
        assert _count_total_references(p) == 4

    def test_papers_with_referenced_works(self, tmp_path):
        p = tmp_path / "corpus.jsonl"
        lines = [
            json.dumps({"title": "A", "referenced_works": ["w1", "w2"]}),
        ]
        p.write_text("\n".join(lines) + "\n")
        assert _count_total_references(p) == 2

    def test_malformed_line_skipped(self, tmp_path):
        p = tmp_path / "corpus.jsonl"
        p.write_text('{"title":"A","references":["r1"]}\nnot-json\n')
        assert _count_total_references(p) == 1


# ── _load_json ──────────────────────────────────────────────────────────


class TestLoadJson:
    """Test JSON file loader."""

    def test_missing_file(self, tmp_path):
        missing = tmp_path / "missing.json"
        result = _load_json(missing)
        assert isinstance(result, dict)
        assert "_error" in result
        assert "file_not_found" in result["_error"]

    def test_valid_json(self, tmp_path):
        p = tmp_path / "data.json"
        p.write_text('{"key": "value"}')
        result = _load_json(p)
        assert result == {"key": "value"}


# ── compute_variables (full pipeline output) ────────────────────────────


def _write_pipeline_output(output_dir: Path) -> None:
    """Write complete pipeline output for testing compute_variables."""
    # corpus.jsonl (3 papers)
    corpus = [
        json.dumps({
            "title": "Paper A", "references": ["r1", "r2"],
        }),
        json.dumps({
            "title": "Paper B", "references": ["r3"],
        }),
        json.dumps({
            "title": "Paper C", "references": [],
        }),
    ]
    (output_dir / "corpus.jsonl").write_text("\n".join(corpus) + "\n")

    # temporal_analysis.json
    temporal = {
        "year_counts": {"2020": 1, "2021": 1, "2022": 1},
        "cumulative": {"2020": 1, "2021": 2, "2022": 3},
        "first_year": 2020,
        "last_year": 2022,
        "peak_year": 2022,
        "total_papers": 3,
        "mean_growth_rate": 0.5,
        "doubling_time": 1.4,
        "cagr": 0.26,
    }
    (output_dir / "temporal_analysis.json").write_text(json.dumps(temporal))

    # citation_network.json
    citation = {
        "num_nodes": 3,
        "num_edges": 2,
        "density": 0.333,
        "avg_in_degree": 0.67,
        "connected_components": 1,
        "num_communities": 1,
        "total_references": 3,
        "top_pagerank": {"paper_a": 0.4, "paper_b": 0.35},
    }
    (output_dir / "citation_network.json").write_text(json.dumps(citation))

    # subfield_classification.json
    subfield = {
        "A1_formal": 10,
        "A2_philosophy": 8,
        "B_tools": 15,
        "C1_neuroscience": 12,
        "C2_robotics": 9,
        "C3_language": 5,
        "C4_psychiatry": 3,
        "C5_biology": 7,
    }
    (output_dir / "subfield_classification.json").write_text(json.dumps(subfield))

    # assertion_summary.json
    assertion = {
        "total_assertions": 45,
        "type_counts": {"supports": 20, "contradicts": 10, "neutral": 15},
        "per_hypothesis": {
            "FEP_UNIVERSALITY": {"supports": 5, "contradicts": 2, "neutral": 3},
        },
    }
    (output_dir / "assertion_summary.json").write_text(json.dumps(assertion))

    # hypothesis_scores.json
    scores = {
        "FEP_UNIVERSALITY": 0.82,
        "AIF_OPTIMALITY": 0.5,
        "MARKOV_BLANKET_REALISM": -0.1,
    }
    (output_dir / "hypothesis_scores.json").write_text(json.dumps(scores))

    # topics.json
    topics = [
        {"topic_id": 0, "top_words": ["agent", "model"], "weights": [0.06, 0.05]},
        {"topic_id": 1, "top_words": ["free", "energy"], "weights": [0.07, 0.04]},
    ]
    (output_dir / "topics.json").write_text(json.dumps(topics))

    # figures directory with sample PNGs
    fig_dir = output_dir / "figures"
    fig_dir.mkdir(exist_ok=True)
    for name in ["field_summary.png", "growth_curve.png", "hypothesis_dashboard.png"]:
        (fig_dir / name).write_bytes(b"\x89PNG")


class TestComputeVariables:
    """Test compute_variables with various pipeline output states."""

    def test_full_output(self, tmp_path):
        _write_pipeline_output(tmp_path)
        variables = compute_variables(tmp_path)

        # Corpus size
        assert variables["CORPUS_SIZE"] == "3"
        assert variables["CORPUS_SIZE_LATEX"] == "3"

        # Temporal
        assert variables["YEAR_START"] == "2020"
        assert variables["YEAR_END"] == "2022"
        assert variables["PEAK_YEAR"] == "2022"
        assert variables["PEAK_YEAR_COUNT"] == "1"
        assert "CAGR_PCT" in variables
        assert "MEAN_YOY_GROWTH_PCT" in variables
        assert "DOUBLING_TIME" in variables

        # Citation
        assert variables["CITATION_EDGES"] == "2"
        assert variables["CITATION_NODES"] == "3"
        assert variables["CITATION_COMPONENTS"] == "1"
        assert "CITATION_DENSITY_PCT" in variables
        assert variables["MEAN_IN_DEGREE"] == "0.7"
        assert variables["CITATION_TOTAL_REFS"] == "3"
        assert "CITATION_RESOLUTION_PCT" in variables

        # Subfield
        assert variables["A1_COUNT"] == "10"
        assert variables["A2_COUNT"] == "8"
        assert variables["B_COUNT"] == "15"
        assert variables["C1_COUNT"] == "12"
        assert variables["A_COUNT"] == "18"  # A1 + A2
        assert "A_PCT" in variables
        assert "C_COUNT" in variables

        # Assertions
        assert variables["TOTAL_ASSERTIONS"] == "45"

        # Hypothesis scores
        assert variables["FEP_UNIVERSALITY_SCORE"] == "+0.82"
        assert variables["MARKOV_BLANKET_REALISM_SCORE"] == "-0.10"

        # Topics
        assert variables["NUM_TOPICS"] == "2"

        # Figures
        assert variables["NUM_FIGURES"] == "3"

    def test_empty_output_dir(self, tmp_path):
        """compute_variables handles a completely empty output directory."""
        variables = compute_variables(tmp_path)
        assert variables["CORPUS_SIZE"] == "0"
        assert variables["CORPUS_SIZE_LATEX"] == "0"
        # Should have at least corpus-size variables
        assert len(variables) >= 2

    def test_partial_output(self, tmp_path):
        """compute_variables handles partial pipeline output."""
        (tmp_path / "corpus.jsonl").write_text('{"title":"A"}\n')
        variables = compute_variables(tmp_path)
        assert variables["CORPUS_SIZE"] == "1"
        # No temporal data, so temporal variables should be absent
        assert "YEAR_START" not in variables

    def test_citation_without_total_refs(self, tmp_path):
        """Citation variables compute from corpus when total_references=0."""
        (tmp_path / "corpus.jsonl").write_text(
            json.dumps({"title": "A", "references": ["r1", "r2"]}) + "\n"
        )
        citation = {
            "num_nodes": 1,
            "num_edges": 2,
            "density": 0.5,
            "avg_in_degree": 2.0,
            "connected_components": 1,
            "total_references": 0,  # Force fallback to corpus counting
        }
        (tmp_path / "citation_network.json").write_text(json.dumps(citation))
        variables = compute_variables(tmp_path)
        assert variables["CITATION_TOTAL_REFS"] == "2"

    def test_citation_no_refs_anywhere(self, tmp_path):
        """Citation variables when no references in corpus or JSON."""
        (tmp_path / "corpus.jsonl").write_text(
            json.dumps({"title": "A"}) + "\n"
        )
        citation = {
            "num_nodes": 1,
            "num_edges": 0,
            "density": 0.0,
            "avg_in_degree": 0.0,
            "connected_components": 1,
            "total_references": 0,
        }
        (tmp_path / "citation_network.json").write_text(json.dumps(citation))
        variables = compute_variables(tmp_path)
        assert variables["CITATION_TOTAL_REFS"] == "0"
        assert variables["CITATION_RESOLUTION_PCT"] == "0.0"

    def test_no_figures_dir(self, tmp_path):
        """NUM_FIGURES defaults when figures/ doesn't exist."""
        (tmp_path / "corpus.jsonl").write_text("")
        variables = compute_variables(tmp_path)
        assert variables["NUM_FIGURES"] == "16"

    def test_hypothesis_scores_dict_format(self, tmp_path):
        """Handle hypothesis scores in nested dict format."""
        (tmp_path / "corpus.jsonl").write_text("")
        scores = {"FEP_UNIVERSALITY": {"score": 0.75, "ci_low": 0.6}}
        (tmp_path / "hypothesis_scores.json").write_text(json.dumps(scores))
        variables = compute_variables(tmp_path)
        assert variables["FEP_UNIVERSALITY_SCORE"] == "+0.75"

    def test_cagr_large_value(self, tmp_path):
        """CAGR_PCT always formatted as a percentage (multiplied by 100).
        cagr=1.5 means 150% annual growth, displayed as '150.00'."""
        (tmp_path / "corpus.jsonl").write_text("")
        temporal = {
            "year_counts": {"2020": 10},
            "cumulative": {"2020": 10},
            "first_year": 2020, "last_year": 2020,
            "peak_year": 2020, "total_papers": 10,
            "mean_growth_rate": 1.5,
            "doubling_time": 0.5,
            "cagr": 1.5,
        }
        (tmp_path / "temporal_analysis.json").write_text(json.dumps(temporal))
        variables = compute_variables(tmp_path)
        assert variables["CAGR_PCT"] == "150.00"
        assert variables["MEAN_YOY_GROWTH_PCT"] == "150.0"

    def test_doubling_time_zero(self, tmp_path):
        """DOUBLING_TIME empty string when zero."""
        (tmp_path / "corpus.jsonl").write_text("")
        temporal = {
            "year_counts": {"2020": 10},
            "cumulative": {"2020": 10},
            "first_year": 2020, "last_year": 2020,
            "peak_year": 2020, "total_papers": 10,
            "mean_growth_rate": 0.1,
            "doubling_time": 0,
            "cagr": 0.1,
        }
        (tmp_path / "temporal_analysis.json").write_text(json.dumps(temporal))
        variables = compute_variables(tmp_path)
        assert variables["DOUBLING_TIME"] == ""

    def test_subfield_with_zero_total(self, tmp_path):
        """Subfield percentages handle all-zero counts."""
        (tmp_path / "corpus.jsonl").write_text("")
        subfield = {
            "A1_formal": 0, "A2_philosophy": 0, "B_tools": 0,
            "C1_neuroscience": 0, "C2_robotics": 0, "C3_language": 0,
            "C4_psychiatry": 0, "C5_biology": 0,
        }
        (tmp_path / "subfield_classification.json").write_text(json.dumps(subfield))
        variables = compute_variables(tmp_path)
        assert variables["A1_COUNT"] == "0"
        assert variables["A_PCT"] == "0.0"

    def test_assertion_pct_computed(self, tmp_path):
        """ASSERTION_SUPPORT_PCT and ASSERTION_CONTRADICT_PCT computed from type_counts."""
        (tmp_path / "corpus.jsonl").write_text("")
        assertion = {
            "total_assertions": 40,
            "type_counts": {"supports": 20, "contradicts": 5, "neutral": 15},
        }
        (tmp_path / "assertion_summary.json").write_text(json.dumps(assertion))
        variables = compute_variables(tmp_path)
        # (20/(20+5))*100 = 80.0%; (5/(20+5))*100 = 20.0%
        assert variables["ASSERTION_SUPPORT_PCT"] == "80.0"
        assert variables["ASSERTION_CONTRADICT_PCT"] == "20.0"

    def test_assertion_pct_zero_when_no_support_or_contradict(self, tmp_path):
        """Assertion percentages are 0.0 when supports=0 and contradicts=0."""
        (tmp_path / "corpus.jsonl").write_text("")
        assertion = {
            "total_assertions": 15,
            "type_counts": {"supports": 0, "contradicts": 0, "neutral": 15},
        }
        (tmp_path / "assertion_summary.json").write_text(json.dumps(assertion))
        variables = compute_variables(tmp_path)
        assert variables["ASSERTION_SUPPORT_PCT"] == "0.0"
        assert variables["ASSERTION_CONTRADICT_PCT"] == "0.0"

    def test_assertion_pct_not_produced_when_missing(self, tmp_path):
        """ASSERTION_*_PCT keys absent when assertion_summary.json is missing."""
        (tmp_path / "corpus.jsonl").write_text("")
        variables = compute_variables(tmp_path)
        assert "ASSERTION_SUPPORT_PCT" not in variables
        assert "ASSERTION_CONTRADICT_PCT" not in variables


# ── inject_variables ────────────────────────────────────────────────────


class TestInjectVariables:
    """Test template variable injection."""

    def test_basic_replacement(self):
        content = "The corpus contains {{CORPUS_SIZE}} papers."
        variables = {"CORPUS_SIZE": "775"}
        result = inject_variables(content, variables, filename="test.md")
        assert result == "The corpus contains 775 papers."

    def test_multiple_replacements(self):
        content = "From {{YEAR_START}} to {{YEAR_END}}."
        variables = {"YEAR_START": "2010", "YEAR_END": "2024"}
        result = inject_variables(content, variables)
        assert result == "From 2010 to 2024."

    def test_unresolved_variable_kept(self):
        content = "Size: {{CORPUS_SIZE}}, Unknown: {{UNKNOWN_VAR}}"
        variables = {"CORPUS_SIZE": "42"}
        result = inject_variables(content, variables, lenient=True)
        assert "42" in result
        assert "{{UNKNOWN_VAR}}" in result

    def test_no_variables(self):
        content = "No placeholders here."
        result = inject_variables(content, {})
        assert result == content

    def test_empty_content(self):
        result = inject_variables("", {"CORPUS_SIZE": "42"})
        assert result == ""

    def test_repeated_variable(self):
        content = "{{SIZE}} and another {{SIZE}}"
        variables = {"SIZE": "100"}
        result = inject_variables(content, variables)
        assert result == "100 and another 100"

    def test_latex_formatted_value(self):
        content = "$N = {{CORPUS_SIZE_LATEX}}$ papers"
        variables = {"CORPUS_SIZE_LATEX": "1,834"}
        result = inject_variables(content, variables, filename="abstract.md")
        assert result == "$N = 1,834$ papers"


# ── H1–H8 alias mapping ──────────────────────────────────────────────────


class TestHypothesisAliasMapping:
    """Test that H1-H8 short aliases are correctly created from full IDs."""

    def test_h1_alias_created(self, tmp_path):
        """H1_SCORE should be created from FEP_UNIVERSALITY_SCORE."""
        (tmp_path / "corpus.jsonl").write_text("")
        scores = {"FEP_UNIVERSALITY": 0.82}
        (tmp_path / "hypothesis_scores.json").write_text(json.dumps(scores))
        variables = compute_variables(tmp_path)
        assert variables.get("H1_SCORE") == "+0.82"
        assert variables.get("FEP_UNIVERSALITY_SCORE") == "+0.82"

    def test_h3_alias_created(self, tmp_path):
        """H3_SCORE should map from MARKOV_BLANKET_REALISM_SCORE."""
        (tmp_path / "corpus.jsonl").write_text("")
        scores = {"MARKOV_BLANKET_REALISM": -0.15}
        (tmp_path / "hypothesis_scores.json").write_text(json.dumps(scores))
        variables = compute_variables(tmp_path)
        assert variables.get("H3_SCORE") == "-0.15"

    def test_assertion_aliases(self, tmp_path):
        """H1_SUPPORT etc. created from full assertion summary keys."""
        (tmp_path / "corpus.jsonl").write_text("")
        assertion = {
            "total_assertions": 10,
            "per_hypothesis": {
                "FEP_UNIVERSALITY": {"supports": 5, "contradicts": 2, "neutral": 3},
            },
        }
        (tmp_path / "assertion_summary.json").write_text(json.dumps(assertion))
        variables = compute_variables(tmp_path)
        assert variables.get("H1_SUPPORT") == "5"
        assert variables.get("H1_CONTRADICT") == "2"
        assert variables.get("H1_NEUTRAL") == "3"
        assert variables.get("H1_TOTAL") == "10"

    def test_tfidf_default(self, tmp_path):
        """NUM_VOCAB_FEATURES defaults to 500 when tfidf_data.json missing."""
        (tmp_path / "corpus.jsonl").write_text("")
        variables = compute_variables(tmp_path)
        assert variables["NUM_VOCAB_FEATURES"] == "500"

    def test_tfidf_from_data(self, tmp_path):
        """NUM_VOCAB_FEATURES computed from tfidf_data.json feature_names."""
        (tmp_path / "corpus.jsonl").write_text("")
        tfidf = {"feature_names": ["word1", "word2", "word3"]}
        (tmp_path / "tfidf_data.json").write_text(json.dumps(tfidf))
        variables = compute_variables(tmp_path)
        assert variables["NUM_VOCAB_FEATURES"] == "3"
        assert variables["NUM_VOCAB_FEATURES_LATEX"] == "3"

    def test_data_subdir_fallback(self, tmp_path):
        """Variables are loaded from data/ subdirectory when present."""
        data_dir = tmp_path / "data"
        data_dir.mkdir()
        # Put corpus in data/
        (data_dir / "corpus.jsonl").write_text('{"title":"A"}\n{"title":"B"}\n')
        variables = compute_variables(tmp_path)
        assert variables["CORPUS_SIZE"] == "2"

    def test_manuscript_manifest_records_tokens_and_hashes(self, tmp_path):
        manuscript = tmp_path / "manuscript"
        manuscript.mkdir()
        (manuscript / "00_abstract.md").write_text("N={{CORPUS_SIZE}}", encoding="utf-8")
        (manuscript / "AGENTS.md").write_text("{{NOT_A_VARIABLE}}", encoding="utf-8")
        output = tmp_path / "output"
        (output / "data").mkdir(parents=True)
        (output / "figures").mkdir()
        (output / "data" / "corpus.jsonl").write_text("{}\n", encoding="utf-8")
        assert collect_manuscript_tokens(manuscript) == {"CORPUS_SIZE": ["00_abstract.md"]}
        path = write_manuscript_variables(output, tmp_path, {"CORPUS_SIZE": "1"})
        payload = json.loads(path.read_text(encoding="utf-8"))
        assert payload["source_tokens"]["CORPUS_SIZE"] == ["00_abstract.md"]
        assert payload["source_files"]
