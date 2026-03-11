"""Tests for analysis.subfield_classifier module.

Validates keyword-based domain classification using papers
with titles and abstracts targeting specific Active Inference domains
(A1–A2, B, C1–C5).
"""

import textwrap
from pathlib import Path

import pytest

from analysis.subfield_classifier import (
    DEFAULT_SUBFIELDS,
    SUBFIELDS,
    _get_default_field,
    classify_corpus,
    classify_paper,
    configure_subfields,
    load_subfields_from_config,
)
from literature.models import Paper


# ── Fixtures ──────────────────────────────────────────────────────────


def _paper(title: str, abstract: str = "") -> Paper:
    """Shorthand to create a Paper with title and abstract."""
    return Paper(title=title, abstract=abstract)


# ── SUBFIELDS constant ───────────────────────────────────────────────


class TestSubfieldsConstant:
    """Tests for the SUBFIELDS dictionary."""

    def test_has_eight_domains(self):
        """Exactly 8 domains defined."""
        assert len(SUBFIELDS) == 8

    def test_each_domain_has_keywords(self):
        """Each domain has a non-empty keywords list."""
        for name, info in SUBFIELDS.items():
            assert "keywords" in info, f"{name} missing keywords"
            assert len(info["keywords"]) > 0, f"{name} has empty keywords"

    def test_each_domain_has_description(self):
        """Each domain has a description string."""
        for name, info in SUBFIELDS.items():
            assert "description" in info, f"{name} missing description"
            assert isinstance(info["description"], str)

    def test_expected_domain_names(self):
        """All expected domain names are present."""
        expected = {
            "A2_philosophy",
            "A1_formal",
            "B_tools",
            "C1_neuroscience",
            "C2_robotics",
            "C3_language",
            "C4_psychiatry",
            "C5_biology",
        }
        assert set(SUBFIELDS.keys()) == expected

    def test_each_domain_has_priority(self):
        """Each domain has a priority integer."""
        for name, info in SUBFIELDS.items():
            assert "priority" in info, f"{name} missing priority"
            assert isinstance(info["priority"], int)

    def test_a2_has_lowest_priority(self):
        """A2_philosophy should have the lowest (highest number) priority."""
        a2_priority = SUBFIELDS["A2_philosophy"]["priority"]
        for name, info in SUBFIELDS.items():
            if name != "A2_philosophy":
                assert info["priority"] <= a2_priority, (
                    f"{name} has priority {info['priority']} >= A2's {a2_priority}"
                )

    def test_application_domains_have_highest_priority(self):
        """C1-C5 should have priority 1 (highest specificity)."""
        for name in ["C1_neuroscience", "C2_robotics", "C3_language",
                      "C4_psychiatry", "C5_biology"]:
            assert SUBFIELDS[name]["priority"] == 1, (
                f"{name} should have priority 1, got {SUBFIELDS[name]['priority']}"
            )


# ── classify_paper ───────────────────────────────────────────────────


class TestClassifyPaper:
    """Tests for classify_paper."""

    def test_philosophy_domain(self):
        """Paper about FEP conceptually (no math) maps to A2_philosophy."""
        paper = _paper(
            title="The Free Energy Principle and Consciousness",
            abstract="We discuss the phenomenology of predictive processing and bayesian brain hypothesis from an enactivism perspective",
        )
        assert classify_paper(paper) == "A2_philosophy"

    def test_formal_theory_with_equations(self):
        """Paper with mathematical formalism maps to A1_formal."""
        paper = _paper(
            title="A Variational Free Energy Formulation",
            abstract="We derive a theorem proving convergence of the variational bound via KL divergence optimization on a manifold",
        )
        assert classify_paper(paper) == "A1_formal"

    def test_formal_theory_with_bayesian_math(self):
        """Paper with Bayesian inference formalism maps to A1_formal."""
        paper = _paper(
            title="Active Inference as Posterior Optimization",
            abstract="We present a derivation showing the posterior distribution under the generative model with Laplace approximation and message passing",
        )
        assert classify_paper(paper) == "A1_formal"

    def test_robotics_domain(self):
        """Paper about robot navigation maps to C2_robotics."""
        paper = _paper(
            title="Robot Navigation Using Active Inference",
            abstract="We present a robot that uses sensorimotor control for navigation and manipulation",
        )
        assert classify_paper(paper) == "C2_robotics"

    def test_neuroscience_domain(self):
        """Paper about cortical processing maps to C1_neuroscience."""
        paper = _paper(
            title="Cortical Predictive Processing in the Brain",
            abstract="Using fMRI and EEG we study neural synaptic dopamine mechanisms in hippocampal circuits",
        )
        assert classify_paper(paper) == "C1_neuroscience"

    def test_psychiatry_domain(self):
        """Paper about schizophrenia maps to C4_psychiatry."""
        paper = _paper(
            title="Computational Psychiatry of Schizophrenia",
            abstract="We model psychosis and depression through clinical autism assessments",
        )
        assert classify_paper(paper) == "C4_psychiatry"

    def test_formal_theory_domain(self):
        """Paper about Markov blankets with stochastic math maps to A1_formal."""
        paper = _paper(
            title="Markov Blanket Formalism",
            abstract="Information geometry and path integral formulation with stochastic langevin dynamics",
        )
        assert classify_paper(paper) == "A1_formal"

    def test_biology_domain(self):
        """Paper about morphogenesis maps to C5_biology."""
        paper = _paper(
            title="Morphogenesis and the Free Energy Principle",
            abstract="Cell organism evolution and autopoiesis in biological systems and life",
        )
        assert classify_paper(paper) == "C5_biology"

    def test_language_domain(self):
        """Paper about language processing maps to C3_language."""
        paper = _paper(
            title="Language Processing Under Active Inference",
            abstract="Linguistic speech and semantic reading for communication and natural language understanding",
        )
        assert classify_paper(paper) == "C3_language"

    def test_tools_domain(self):
        """Paper about deep active inference maps to B_tools."""
        paper = _paper(
            title="Deep Active Inference for Scalable Planning",
            abstract="Amortized planning with monte carlo tree search and reinforcement learning benchmarks",
        )
        assert classify_paper(paper) == "B_tools"

    def test_no_keywords_defaults_to_philosophy(self):
        """Paper with no matching keywords defaults to A2_philosophy."""
        paper = _paper(
            title="Unrelated Topic About Cooking",
            abstract="How to make pasta with tomato sauce and basil",
        )
        assert classify_paper(paper) == "A2_philosophy"

    def test_case_insensitive(self):
        """Matching is case-insensitive."""
        paper = _paper(
            title="ROBOT NAVIGATION USING EMBODIED MOTOR CONTROL",
            abstract="SENSORIMOTOR MANIPULATION",
        )
        assert classify_paper(paper) == "C2_robotics"

    def test_specific_domain_wins_over_general(self):
        """When C-domain keywords and A1/A2 keywords both match, C wins."""
        # Has both neuroscience and formal theory keywords
        paper = _paper(
            title="Neural Cortical Free Energy Principle Formulation",
            abstract="We derive a theorem for cortical prediction error in hippocampal fMRI data",
        )
        assert classify_paper(paper) == "C1_neuroscience"

    def test_a1_wins_over_a2(self):
        """Formal theory (A1) wins over philosophy (A2) when both match."""
        paper = _paper(
            title="Free Energy Principle as Variational Inference",
            abstract="We present a theorem showing convergence of the posterior under the generative model",
        )
        assert classify_paper(paper) == "A1_formal"

    def test_abstract_contributes_to_match(self):
        """Keywords in abstract count toward matching."""
        paper = _paper(
            title="A New Framework",
            abstract="This paper presents a robot navigation system with motor control",
        )
        assert classify_paper(paper) == "C2_robotics"

    def test_tools_wins_over_formal_theory(self):
        """Tools (B, priority 2) wins over formal theory (A1, priority 3)."""
        paper = _paper(
            title="Scalable Deep Active Inference for Planning",
            abstract="We benchmark our amortized algorithm with monte carlo tree search against reinforcement learning",
        )
        assert classify_paper(paper) == "B_tools"

    def test_pure_fep_paper_goes_to_a1_if_math_present(self):
        """FEP paper WITH mathematical formalism → A1 (math wins over catch-all)."""
        paper = _paper(
            title="The Free Energy Principle: A Mathematical Derivation",
            abstract="We present a proof of convergence for the variational bound with equation for the posterior",
        )
        assert classify_paper(paper) == "A1_formal"

    def test_pure_fep_paper_goes_to_a2_if_no_math(self):
        """FEP paper WITHOUT mathematical formalism → A2 (catch-all)."""
        paper = _paper(
            title="Understanding Active Inference",
            abstract="A review of the free energy principle and its implications for generative model approaches",
        )
        assert classify_paper(paper) == "A2_philosophy"


# ── classify_corpus ──────────────────────────────────────────────────


class TestClassifyCorpus:
    """Tests for classify_corpus."""

    def test_all_domains_present_in_output(self):
        """Output dict has all 8 domain keys."""
        papers = [_paper("Some paper")]
        result = classify_corpus(papers)
        assert set(result.keys()) == set(SUBFIELDS.keys())

    def test_papers_distributed_correctly(self):
        """Papers are assigned to the correct domain lists."""
        papers = [
            _paper("Robot Navigation", "robot motor control"),
            _paper("Brain Cortex Study", "neural cortical fmri eeg"),
            _paper("Pasta Recipe", "cooking with tomatoes"),
        ]
        result = classify_corpus(papers)

        assert papers[0] in result["C2_robotics"]
        assert papers[1] in result["C1_neuroscience"]
        assert papers[2] in result["A2_philosophy"]  # default

    def test_total_papers_preserved(self):
        """Total papers across all domains equals input count."""
        papers = [
            _paper("Robot Navigation", "robot motor control"),
            _paper("Brain Cortex Study", "neural cortical fmri eeg"),
            _paper("A Theorem on Convergence", "proof of posterior convergence with equation"),
            _paper("Schizophrenia Model", "psychiatric schizophrenia depression"),
            _paper("Cooking", "nothing relevant here"),
        ]
        result = classify_corpus(papers)
        total = sum(len(ps) for ps in result.values())
        assert total == 5

    def test_empty_corpus(self):
        """Empty input produces empty lists for all domains."""
        result = classify_corpus([])
        for name in SUBFIELDS:
            assert result[name] == []

    def test_all_same_domain(self):
        """All papers with same keywords group together."""
        papers = [
            _paper(f"Robot Paper {i}", "robot motor control") for i in range(5)
        ]
        result = classify_corpus(papers)
        assert len(result["C2_robotics"]) == 5
        for name in SUBFIELDS:
            if name != "C2_robotics":
                assert len(result[name]) == 0


# ── load_subfields_from_config ───────────────────────────────────────


class TestLoadSubfieldsFromConfig:
    """Tests for YAML-based subfield configuration."""

    def test_valid_config(self, tmp_path: Path):
        """Config with valid subfield_keywords is loaded correctly."""
        config = tmp_path / "config.yaml"
        config.write_text(textwrap.dedent("""\
            subfield_keywords:
              C1_neuro:
                - brain
                - cortex
              B_tools:
                - deep learning
                - benchmark
        """))
        result = load_subfields_from_config(config)
        assert "C1_neuro" in result
        assert "B_tools" in result
        assert result["C1_neuro"]["keywords"] == ["brain", "cortex"]
        assert result["C1_neuro"]["priority"] == 1  # C-prefix → priority 1
        assert result["B_tools"]["priority"] == 2   # B-prefix → priority 2

    def test_missing_section_falls_back_to_defaults(self, tmp_path: Path):
        """Config without subfield_keywords returns defaults."""
        config = tmp_path / "config.yaml"
        config.write_text("other_key: value\n")
        result = load_subfields_from_config(config)
        assert result == dict(DEFAULT_SUBFIELDS)

    def test_nonexistent_file_falls_back_to_defaults(self, tmp_path: Path):
        """Non-existent config file returns defaults."""
        config = tmp_path / "does_not_exist.yaml"
        result = load_subfields_from_config(config)
        assert result == dict(DEFAULT_SUBFIELDS)

    def test_malformed_entry_skipped(self, tmp_path: Path):
        """Non-list keyword entries are skipped with warning."""
        config = tmp_path / "config.yaml"
        config.write_text(textwrap.dedent("""\
            subfield_keywords:
              C1_neuro:
                - brain
              bad_entry: "not a list"
        """))
        result = load_subfields_from_config(config)
        assert "C1_neuro" in result
        assert "bad_entry" not in result

    def test_empty_keywords_falls_back_to_defaults(self, tmp_path: Path):
        """Config with empty subfield_keywords dict returns defaults."""
        config = tmp_path / "config.yaml"
        config.write_text("subfield_keywords: {}\n")
        result = load_subfields_from_config(config)
        assert result == dict(DEFAULT_SUBFIELDS)


# ── configure_subfields ──────────────────────────────────────────────


class TestConfigureSubfields:
    """Tests for configure_subfields."""

    def test_with_config_path(self, tmp_path: Path):
        """configure_subfields loads from config and sets module SUBFIELDS."""
        config = tmp_path / "config.yaml"
        config.write_text(textwrap.dedent("""\
            subfield_keywords:
              C1_test:
                - test_keyword
        """))
        result = configure_subfields(config)
        assert "C1_test" in result
        # Restore defaults after test
        configure_subfields(None)

    def test_without_config_path_uses_defaults(self):
        """configure_subfields(None) resets to DEFAULT_SUBFIELDS."""
        result = configure_subfields(None)
        assert result == dict(DEFAULT_SUBFIELDS)


# ── _get_default_field ───────────────────────────────────────────────


class TestGetDefaultField:
    """Tests for _get_default_field."""

    def test_returns_philosophy_catch_all(self):
        """Default field is the philosophy/catch-all domain."""
        result = _get_default_field()
        # Should be a domain with 'free energy principle' or 'active inference'
        assert result in SUBFIELDS
        keywords = [k.lower() for k in SUBFIELDS[result]["keywords"]]
        assert "free energy principle" in keywords or "active inference" in keywords

