"""Literature search pipeline (multi-source retrieval and corpus persistence)."""

from __future__ import annotations

import argparse
import logging
import time
from pathlib import Path
from typing import Callable

from config import OUTPUT_DIR as DEFAULT_OUTPUT_DIR
from config_loader import load_search_config
from literature.corpus import Corpus
from literature.models import Paper


def search_source(
    source_name: str,
    search_fn: Callable[..., list[Paper]],
    query: str,
    max_results: int,
    corpus: Corpus,
    logger: logging.Logger,
) -> str | None:
    """Search one API source and merge papers into *corpus*."""
    t0 = time.monotonic()
    try:
        logger.info("Searching %s for: %s (max %d)", source_name, query[:80], max_results)
        papers = search_fn(query, max_results=max_results)
        before_count = len(corpus)
        for paper in papers:
            corpus.add(paper)
        new_papers = len(corpus) - before_count
        duplicates = len(papers) - new_papers
        elapsed = time.monotonic() - t0
        logger.info(
            "  %s: %d fetched, %d new, %d duplicates (%.1fs)",
            source_name,
            len(papers),
            new_papers,
            duplicates,
            elapsed,
        )
        return f"{source_name} ({len(papers)} papers, {new_papers} new)"
    except Exception as exc:
        elapsed = time.monotonic() - t0
        logger.error("  %s search failed after %.1fs: %s", source_name, elapsed, exc)
        return None


def apply_relevance_filter(
    corpus: Corpus,
    keywords: list[str],
    logger: logging.Logger,
) -> None:
    """Drop papers whose title+abstract lack any *keywords*."""
    pre_filter = len(corpus)
    to_remove: list[str] = []
    for paper in corpus.papers:
        text = (paper.title + " " + paper.abstract).lower()
        if not any(kw in text for kw in keywords):
            to_remove.append(paper.canonical_id)
    for cid in to_remove:
        corpus.remove(cid)
    if to_remove:
        logger.info(
            "Relevance filter: removed %d off-topic papers (%d → %d)",
            len(to_remove),
            pre_filter,
            len(corpus),
        )


def _fast_delay() -> Callable[[float], None]:
    return lambda _seconds: None


def _arxiv_search_fn(
    base_url: str | None,
    *,
    fast: bool,
) -> Callable[..., list[Paper]]:
    from literature.arxiv_client import ARXIV_API_URL, DEFAULT_RATE_LIMIT_SECONDS, search_arxiv

    url = base_url or ARXIV_API_URL
    delay = _fast_delay() if fast else None
    rate_limit = 0.0 if fast else DEFAULT_RATE_LIMIT_SECONDS

    def _search(query: str, max_results: int = 100) -> list[Paper]:
        return search_arxiv(
            query,
            max_results=max_results,
            base_url=url,
            rate_limit_seconds=rate_limit,
            delay_override=delay,
        )

    return _search


def _semantic_scholar_search_fn(
    base_url: str | None,
    *,
    fast: bool,
) -> Callable[..., list[Paper]]:
    from literature.semantic_scholar import S2_API_URL, search_semantic_scholar

    url = base_url or S2_API_URL
    delay = _fast_delay() if fast else None

    def _search(query: str, max_results: int = 100) -> list[Paper]:
        return search_semantic_scholar(
            query,
            max_results=max_results,
            base_url=url,
            delay_override=delay,
        )

    return _search


def _openalex_search_fn(
    base_url: str | None,
    *,
    fast: bool,
) -> Callable[..., list[Paper]]:
    from literature.openalex_client import OPENALEX_API_URL, search_openalex

    url = base_url or OPENALEX_API_URL
    delay = _fast_delay() if fast else None

    def _search(query: str, max_results: int = 100) -> list[Paper]:
        return search_openalex(
            query,
            max_results=max_results,
            base_url=url,
            delay_override=delay,
        )

    return _search


def run_literature_search(
    args: argparse.Namespace,
    *,
    project_root: Path,
    arxiv_base_url: str | None = None,
    semantic_scholar_base_url: str | None = None,
    openalex_base_url: str | None = None,
) -> Path:
    """Execute literature search; return path to saved corpus JSONL.

    Optional ``*_base_url`` kwargs wire pytest-httpserver endpoints into API
    clients without changing production defaults.
    """
    logger = logging.getLogger("literature_search")
    config_path = Path(args.config) if args.config else project_root / "manuscript" / "config.yaml"
    if config_path.exists():
        cfg = load_search_config(config_path)
        if cfg.get("query"):
            args.query = cfg["query"]
        if cfg.get("max_results"):
            args.max_results = cfg["max_results"]
        if cfg.get("resume") is not None:
            args.resume = cfg["resume"]
        if cfg.get("clear_corpus") is not None:
            args.clear_corpus = cfg["clear_corpus"]
        if cfg.get("start_year") is not None and args.start_year is None:
            args.start_year = cfg["start_year"]
        arxiv_queries = cfg["arxiv_queries"]
        relevance_keywords = cfg["relevance_keywords"]
    else:
        from config import DEFAULT_ARXIV_QUERIES, DEFAULT_RELEVANCE_KEYWORDS

        arxiv_queries = list(DEFAULT_ARXIV_QUERIES)
        relevance_keywords = list(DEFAULT_RELEVANCE_KEYWORDS)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = data_dir / "corpus.jsonl"

    if args.clear_corpus and corpus_path.exists():
        corpus_path.unlink()
        logger.info("Cleared existing corpus: %s", corpus_path)

    if args.resume and corpus_path.exists():
        min_year = args.start_year
        corpus = Corpus.load(corpus_path, min_year=min_year)
        logger.info("Resumed existing corpus with %d papers from %s", len(corpus), corpus_path)
        if len(corpus) > 0 and not args.clear_corpus:
            logger.info(
                "Corpus already populated (%d papers) — skipping network searches.",
                len(corpus),
            )
            corpus.save(corpus_path)
            print(str(corpus_path))
            return corpus_path
    else:
        corpus = Corpus()

    sources_searched: list[str] = []
    pipeline_start = time.monotonic()

    fast_api = any(
        url is not None
        for url in (arxiv_base_url, semantic_scholar_base_url, openalex_base_url)
    )

    if not args.skip_arxiv:
        arxiv_search = _arxiv_search_fn(arxiv_base_url, fast=fast_api)
        arxiv_total_before = len(corpus)
        for i, arxiv_query in enumerate(arxiv_queries, 1):
            logger.info("arXiv query %d/%d: %s", i, len(arxiv_queries), arxiv_query)
            result = search_source(
                f"arXiv[{i}]",
                arxiv_search,
                arxiv_query,
                args.max_results,
                corpus,
                logger,
            )
            if result:
                sources_searched.append(result)
        logger.info(
            "arXiv total: %d new unique papers from %d queries",
            len(corpus) - arxiv_total_before,
            len(arxiv_queries),
        )

    if not args.skip_s2:
        s2_search = _semantic_scholar_search_fn(semantic_scholar_base_url, fast=fast_api)
        result = search_source(
            "Semantic Scholar",
            s2_search,
            args.query,
            args.max_results,
            corpus,
            logger,
        )
        if result:
            sources_searched.append(result)

    if not args.skip_openalex:
        openalex_search = _openalex_search_fn(openalex_base_url, fast=fast_api)
        result = search_source(
            "OpenAlex",
            openalex_search,
            args.query,
            args.max_results,
            corpus,
            logger,
        )
        if result:
            sources_searched.append(result)

    apply_relevance_filter(corpus, relevance_keywords, logger)

    if args.start_year is not None:
        pre_year = len(corpus)
        dropped = corpus.drop_before_year(args.start_year)
        if dropped:
            logger.info(
                "Year filter: removed %d papers published before %d (%d → %d)",
                dropped,
                args.start_year,
                pre_year,
                len(corpus),
            )

    corpus.save(corpus_path)
    total_elapsed = time.monotonic() - pipeline_start
    logger.info("--- Literature Search Summary ---")
    logger.info("Sources: %s", ", ".join(sources_searched) if sources_searched else "None")
    logger.info("Total unique papers: %d", len(corpus))
    logger.info("Corpus saved to: %s", corpus_path)
    logger.info("Total search time: %.1fs", total_elapsed)
    print(str(corpus_path))
    return corpus_path
