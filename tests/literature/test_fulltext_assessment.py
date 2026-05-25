"""Tests for literature.fulltext_assessment."""

from __future__ import annotations

from literature.corpus import Corpus
from literature.fulltext_assessment import assess_corpus
from literature.models import Paper


def test_assess_corpus_reports_coverage(sample_papers: list[Paper]) -> None:
    corpus = Corpus()
    for paper in sample_papers:
        corpus.add(paper)
    report = assess_corpus(corpus)
    assert report["total_papers"] == len(sample_papers)
    assert "abstract_coverage" in report
    assert "pdf_availability" in report
