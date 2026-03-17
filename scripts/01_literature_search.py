#!/usr/bin/env python3
"""Literature search orchestrator.

Thin orchestrator that coordinates literature retrieval from multiple
academic APIs (arXiv, Semantic Scholar, OpenAlex), merges results into
a deduplicated corpus, and persists to JSONL format.

Supports --resume to load an existing corpus before fetching (skipping
already-downloaded papers via deduplication), --log-level for verbosity
control, and --config to load settings from a YAML configuration file.

Uses multiple arXiv query strings for comprehensive FEP/AIF coverage,
and logs per-source statistics including new papers, duplicates, and
elapsed time.

All search and merge logic is imported from src/ modules.
"""

from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path

# Add src/ to path for project imports
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from literature.corpus import Corpus
from literature.models import Paper


# Multiple arXiv queries for comprehensive FEP/Active Inference coverage
ARXIV_QUERIES = [
    'all:"active inference"',
    'all:"free energy principle"',
    'all:"predictive coding" AND all:"free energy"',
    'all:"expected free energy"',
    'all:"variational free energy" AND all:"inference"',
]


def _load_config(config_path: Path) -> dict:
    """Load search configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary with 'query' and 'max_results' keys if found,
        empty dict otherwise.
    """
    try:
        import yaml
    except ImportError:
        logging.getLogger("literature_search").warning(
            "pyyaml not installed; --config flag requires pyyaml"
        )
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    search_cfg = data.get("project_config", data).get("search", data.get("search", {}))
    return {
        "query": search_cfg.get("query"),
        "max_results": search_cfg.get("max_results"),
        "resume": search_cfg.get("resume"),
        "clear_corpus": search_cfg.get("clear_corpus"),
        "arxiv_queries": search_cfg.get("arxiv_queries"),
        "relevance_keywords": search_cfg.get("relevance_keywords"),
        "start_year": search_cfg.get("start_year"),
    }


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Search academic databases for Active Inference literature."
    )
    parser.add_argument(
        "--query",
        default="active inference free energy principle",
        help="Search query string (default: 'active inference free energy principle')",
    )
    parser.add_argument(
        "--max-results",
        type=int,
        default=1000,
        help="Maximum results per source (default: 1000)",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT / "output"),
        help="Output directory (default: projects/act_inf_metaanalysis/output/)",
    )
    parser.add_argument(
        "--skip-arxiv",
        action="store_true",
        help="Skip arXiv search",
    )
    parser.add_argument(
        "--skip-s2",
        action="store_true",
        help="Skip Semantic Scholar search",
    )
    parser.add_argument(
        "--skip-openalex",
        action="store_true",
        help="Skip OpenAlex search",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        default=True,
        help="Load existing corpus.jsonl before searching (default: True)",
    )
    parser.add_argument(
        "--clear-corpus",
        action="store_true",
        help="Delete existing corpus before searching (start fresh)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    parser.add_argument(
        "--start-year",
        type=int,
        default=None,
        help="Exclude papers published before this year (default: no filter)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file (overrides --query and --max-results if set)",
    )
    return parser.parse_args()


def _search_source(
    source_name: str,
    search_fn,
    query: str,
    max_results: int,
    corpus: Corpus,
    logger: logging.Logger,
) -> str | None:
    """Search a single source and add papers to corpus with stats logging.

    Args:
        source_name: Human-readable source name for logging.
        search_fn: Callable that takes (query, max_results=) and returns list[Paper].
        query: Search query string.
        max_results: Maximum results to retrieve.
        corpus: Corpus to add papers to.
        logger: Logger instance.

    Returns:
        Summary string like "arXiv (150 papers)" or None on failure.
    """
    t0 = time.monotonic()
    try:
        logger.info("Searching %s for: %s (max %d)", source_name, query[:80], max_results)
        papers = search_fn(query, max_results=max_results)

        before_count = len(corpus)
        for paper in papers:
            corpus.add(paper)
        after_count = len(corpus)

        new_papers = after_count - before_count
        duplicates = len(papers) - new_papers
        elapsed = time.monotonic() - t0

        logger.info(
            "  %s: %d fetched, %d new, %d duplicates (%.1fs)",
            source_name, len(papers), new_papers, duplicates, elapsed,
        )
        return f"{source_name} ({len(papers)} papers, {new_papers} new)"
    except Exception as e:
        elapsed = time.monotonic() - t0
        logger.error("  %s search failed after %.1fs: %s", source_name, elapsed, e)
        return None


def main() -> None:
    """Run literature search pipeline."""
    args = parse_args()

    # Configure logging with user-selected level
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("literature_search")

    # Override from config file if provided
    if args.config:
        cfg = _load_config(Path(args.config))
        if cfg.get("query"):
            args.query = cfg["query"]
            logger.info("Config override: query = %s", args.query)
        if cfg.get("max_results"):
            args.max_results = cfg["max_results"]
            logger.info("Config override: max_results = %d", args.max_results)
        if cfg.get("resume") is not None:
            args.resume = cfg["resume"]
            logger.info("Config override: resume = %s", args.resume)
        if cfg.get("clear_corpus") is not None:
            args.clear_corpus = cfg["clear_corpus"]
            logger.info("Config override: clear_corpus = %s", args.clear_corpus)
        if cfg.get("arxiv_queries"):
            global ARXIV_QUERIES
            ARXIV_QUERIES = cfg["arxiv_queries"]
            logger.info("Config override: arxiv_queries = %d queries", len(ARXIV_QUERIES))
        if cfg.get("start_year") is not None and args.start_year is None:
            args.start_year = cfg["start_year"]
            logger.info("Config override: start_year = %d", args.start_year)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    corpus_path = data_dir / "corpus.jsonl"

    # Clear corpus if requested (explicit fresh start)
    if args.clear_corpus and corpus_path.exists():
        corpus_path.unlink()
        logger.info("Cleared existing corpus: %s", corpus_path)

    # Resume: load existing corpus if present (default: always merge)
    if args.resume and corpus_path.exists():
        corpus = Corpus.load(corpus_path)
        logger.info("Resumed existing corpus with %d papers from %s", len(corpus), corpus_path)
        # If corpus already has data and we're not clearing, skip network searches
        if len(corpus) > 0 and not args.clear_corpus:
            logger.info(
                "Corpus already populated (%d papers) — skipping network searches. "
                "Use --clear-corpus to force a fresh search.",
                len(corpus),
            )
            corpus.save(corpus_path)
            logger.info("--- Literature Search Summary (cached) ---")
            logger.info("Total unique papers: %d", len(corpus))
            logger.info("Corpus saved to: %s", corpus_path)
            print(str(corpus_path))
            return
    else:
        corpus = Corpus()

    sources_searched = []
    pipeline_start = time.monotonic()

    # Search arXiv with multiple queries for comprehensive coverage
    if not args.skip_arxiv:
        from literature.arxiv_client import search_arxiv

        arxiv_total_before = len(corpus)
        for i, arxiv_query in enumerate(ARXIV_QUERIES, 1):
            logger.info("arXiv query %d/%d: %s", i, len(ARXIV_QUERIES), arxiv_query)
            result = _search_source(
                f"arXiv[{i}]", search_arxiv, arxiv_query,
                args.max_results, corpus, logger,
            )
            if result:
                sources_searched.append(result)

        arxiv_total_new = len(corpus) - arxiv_total_before
        logger.info("arXiv total: %d new unique papers from %d queries", arxiv_total_new, len(ARXIV_QUERIES))

    # Search Semantic Scholar
    if not args.skip_s2:
        from literature.semantic_scholar import search_semantic_scholar
        result = _search_source(
            "Semantic Scholar", search_semantic_scholar,
            args.query, args.max_results, corpus, logger,
        )
        if result:
            sources_searched.append(result)

    # Search OpenAlex
    if not args.skip_openalex:
        from literature.openalex_client import search_openalex
        result = _search_source(
            "OpenAlex", search_openalex,
            args.query, args.max_results, corpus, logger,
        )
        if result:
            sources_searched.append(result)

    # Relevance filter: require at least one core keyword in title/abstract
    # Keywords are configurable via YAML config (search.relevance_keywords)
    _CORE_KEYWORDS = [
        "active inference", "free energy principle", "predictive coding",
        "free energy", "variational", "fep", "bayesian brain",
        "markov blanket", "generative model", "predictive processing",
    ]
    if args.config:
        cfg = _load_config(Path(args.config))
        if cfg.get("relevance_keywords"):
            _CORE_KEYWORDS = cfg["relevance_keywords"]
            logger.info("Config override: relevance_keywords = %d keywords", len(_CORE_KEYWORDS))
    pre_filter = len(corpus)
    to_remove = []
    for cid, p in corpus._papers.items():
        text = (p.title + " " + p.abstract).lower()
        if not any(kw in text for kw in _CORE_KEYWORDS):
            to_remove.append(cid)
    for cid in to_remove:
        del corpus._papers[cid]
    if to_remove:
        logger.info(
            "Relevance filter: removed %d off-topic papers (%d → %d)",
            len(to_remove), pre_filter, len(corpus),
        )

    # Year filter: drop papers published before start_year
    if args.start_year is not None:
        pre_year = len(corpus)
        corpus = corpus.filter_by_year(start=args.start_year)
        dropped = pre_year - len(corpus)
        if dropped:
            logger.info(
                "Year filter: removed %d papers published before %d (%d → %d)",
                dropped, args.start_year, pre_year, len(corpus),
            )

    # Save corpus
    corpus.save(corpus_path)

    # Print summary
    total_elapsed = time.monotonic() - pipeline_start
    logger.info("--- Literature Search Summary ---")
    logger.info("Sources: %s", ', '.join(sources_searched) if sources_searched else 'None')
    logger.info("Total unique papers: %d", len(corpus))
    logger.info("Corpus saved to: %s", corpus_path)
    logger.info("Total search time: %.1fs", total_elapsed)
    print(str(corpus_path))


if __name__ == "__main__":
    main()
