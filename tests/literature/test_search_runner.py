"""Tests for literature.search_runner."""

from __future__ import annotations

import argparse
from pathlib import Path

import pytest

from literature.corpus import Corpus
from literature.models import Paper
from literature.search_runner import apply_relevance_filter, run_literature_search, search_source


def _paper(title: str, abstract: str = "active inference study") -> Paper:
    return Paper(title=title, abstract=abstract, authors=[], year=2020)


def test_apply_relevance_filter_removes_off_topic() -> None:
    corpus = Corpus()
    corpus.add(_paper("On topic", "free energy principle analysis"))
    corpus.add(_paper("Off topic", "unrelated gardening methods"))
    apply_relevance_filter(corpus, ["free energy"], __import__("logging").getLogger("test"))
    assert len(corpus) == 1


def test_search_source_adds_papers(tmp_path: Path) -> None:
    corpus = Corpus()
    logger = __import__("logging").getLogger("test")

    def fake_search(_query: str, max_results: int = 100) -> list[Paper]:
        return [_paper("Fetched")]

    result = search_source("Test", fake_search, "query", 10, corpus, logger)
    assert result is not None
    assert len(corpus) == 1


def test_run_literature_search_skips_sources(tmp_output_dir: str) -> None:
    args = argparse.Namespace(
        query="active inference",
        max_results=10,
        output_dir=tmp_output_dir,
        skip_arxiv=True,
        skip_s2=True,
        skip_openalex=True,
        resume=False,
        clear_corpus=False,
        start_year=None,
        config=None,
    )
    project_root = Path(__file__).resolve().parent.parent
    path = run_literature_search(args, project_root=project_root)
    assert path.exists()
