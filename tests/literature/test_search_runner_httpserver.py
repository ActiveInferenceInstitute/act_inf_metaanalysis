"""HTTPServer integration tests for literature.search_runner."""

from __future__ import annotations

import argparse
from pathlib import Path

from pytest_httpserver import HTTPServer

from literature.corpus import Corpus
from literature.search_runner import run_literature_search

ARXIV_ENTRY = """\
<?xml version="1.0" encoding="UTF-8"?>
<feed xmlns="http://www.w3.org/2005/Atom">
  <entry>
    <title>Active Inference Overview</title>
    <summary>Active inference and the free energy principle unify perception and action.</summary>
    <published>2020-01-01T00:00:00Z</published>
  </entry>
</feed>
"""

S2_RESPONSE = {
    "total": 1,
    "data": [
        {
            "paperId": "s2_test_1",
            "title": "Deep Active Inference",
            "abstract": "We study active inference agents using free energy minimization.",
            "year": 2021,
            "authors": [{"name": "Test Author"}],
            "citationCount": 10,
        }
    ],
}

OPENALEX_RESPONSE = {
    "meta": {"count": 1},
    "results": [
        {
            "id": "https://openalex.org/W999",
            "display_name": "OpenAlex Active Inference Paper",
            "publication_year": 2019,
            "abstract_inverted_index": {
                "Active": [0],
                "inference": [1],
                "and": [2],
                "free": [3],
                "energy": [4],
            },
        }
    ],
}


def _base_args(output_dir: Path) -> argparse.Namespace:
    return argparse.Namespace(
        query="active inference",
        max_results=5,
        output_dir=str(output_dir),
        skip_arxiv=False,
        skip_s2=False,
        skip_openalex=False,
        resume=False,
        clear_corpus=False,
        start_year=None,
        config=None,
    )


def test_run_literature_search_arxiv_httpserver(
    httpserver: HTTPServer,
    tmp_path: Path,
) -> None:
    httpserver.expect_request("/api/query").respond_with_data(
        ARXIV_ENTRY,
        content_type="application/atom+xml",
    )
    output_dir = tmp_path / "output"
    args = _base_args(output_dir)
    args.skip_s2 = True
    args.skip_openalex = True

    path = run_literature_search(
        args,
        project_root=tmp_path,
        arxiv_base_url=httpserver.url_for("/api/query"),
    )
    corpus = Corpus.load(path)
    assert len(corpus) >= 1


def test_run_literature_search_all_sources_httpserver(
    httpserver: HTTPServer,
    tmp_path: Path,
) -> None:
    httpserver.expect_request("/api/query").respond_with_data(
        ARXIV_ENTRY,
        content_type="application/atom+xml",
    )
    httpserver.expect_request("/paper/search/bulk").respond_with_json(S2_RESPONSE)
    httpserver.expect_request("/works").respond_with_json(OPENALEX_RESPONSE)

    output_dir = tmp_path / "output"
    args = _base_args(output_dir)
    base = httpserver.url_for("")
    path = run_literature_search(
        args,
        project_root=tmp_path,
        arxiv_base_url=f"{base}/api/query",
        semantic_scholar_base_url=base,
        openalex_base_url=base,
    )
    corpus = Corpus.load(path)
    assert len(corpus) >= 1


def test_run_literature_search_clear_corpus_and_start_year(
    httpserver: HTTPServer,
    tmp_path: Path,
) -> None:
    output_dir = tmp_path / "output"
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True)
    stale_path = data_dir / "corpus.jsonl"
    stale_path.write_text('{"title":"Old"}\n', encoding="utf-8")

    httpserver.expect_request("/api/query").respond_with_data(
        ARXIV_ENTRY,
        content_type="application/atom+xml",
    )

    args = _base_args(output_dir)
    args.clear_corpus = True
    args.start_year = 2020
    args.skip_s2 = True
    args.skip_openalex = True

    path = run_literature_search(
        args,
        project_root=tmp_path,
        arxiv_base_url=httpserver.url_for("/api/query"),
    )
    corpus = Corpus.load(path)
    assert all(paper.year is None or paper.year >= 2020 for paper in corpus.papers)
    assert path == stale_path
