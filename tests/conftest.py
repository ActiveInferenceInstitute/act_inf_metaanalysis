"""Pytest configuration for act_inf_metaanalysis tests."""

import os
import sys
import tempfile

import pytest

# Force headless backend for matplotlib in tests
os.environ.setdefault("MPLBACKEND", "Agg")

# Add src/ to path so we can import project modules
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC = os.path.join(ROOT, "src")
if SRC not in sys.path:
    sys.path.insert(0, SRC)


@pytest.fixture
def sample_papers():
    """Return a list of sample Paper objects for testing."""
    from literature.models import Paper

    return [
        Paper(
            title="Active Inference: A Process Theory",
            abstract="This paper presents active inference as a unified brain theory based on the free energy principle.",
            year=2017,
            doi="10.1162/NECO_a_00912",
            arxiv_id="1709.02341",
            citation_count=500,
            references=["ref_001", "ref_002"],
        ),
        Paper(
            title="Deep Active Inference Agents Using Monte-Carlo Methods",
            abstract="We present deep active inference agents that scale to complex environments using neural networks.",
            year=2020,
            doi="10.5555/deep_aif_2020",
            citation_count=120,
            references=["ref_001"],
        ),
        Paper(
            title="Computational Psychiatry and Active Inference",
            abstract="We model schizophrenia as aberrant precision weighting in clinical psychiatry settings.",
            year=2021,
            doi="10.5555/comp_psych_2021",
            citation_count=45,
            references=[],
        ),
    ]


@pytest.fixture
def sample_assertions():
    """Return a list of sample Assertion objects for testing."""
    from knowledge_graph.nanopublication import Assertion

    return [
        Assertion(
            assertion_id="assert_000001",
            paper_id="paper_001",
            claim="Active inference provides a unified framework.",
            assertion_type="supports",
            hypothesis_id="FEP_UNIVERSALITY",
            confidence=0.9,
            citation_count=500,
        ),
        Assertion(
            assertion_id="assert_000002",
            paper_id="paper_002",
            claim="Deep AIF matches RL performance in discrete tasks.",
            assertion_type="supports",
            hypothesis_id="SCALABILITY",
            confidence=0.7,
            citation_count=120,
        ),
        Assertion(
            assertion_id="assert_000003",
            paper_id="paper_003",
            claim="Markov blanket boundaries are statistical constructs only.",
            assertion_type="contradicts",
            hypothesis_id="MARKOV_BLANKET_REALISM",
            confidence=0.8,
            citation_count=200,
        ),
    ]


@pytest.fixture
def tmp_output_dir():
    """Return a temporary directory for test outputs, cleaned up after test."""
    with tempfile.TemporaryDirectory(prefix="aif_test_") as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_corpus_path(sample_papers, tmp_output_dir):
    """Write sample papers to a temporary JSONL corpus file.

    Returns the path to the created corpus.jsonl file.
    """
    from literature.corpus import Corpus

    corpus = Corpus()
    for paper in sample_papers:
        corpus.add(paper)
    corpus_path = Path(tmp_output_dir) / "corpus.jsonl"
    corpus.save(corpus_path)
    return str(corpus_path)
