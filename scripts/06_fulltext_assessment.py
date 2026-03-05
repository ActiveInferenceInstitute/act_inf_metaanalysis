#!/usr/bin/env python3
"""Full-text availability assessment.

Loads the corpus and produces a report on full-text availability,
including PDF URLs, open access status, and source breakdown.

Outputs:
    - Console summary
    - output/data/fulltext_assessment.json
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from collections import Counter
from pathlib import Path

# Add src/ to path for project imports
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from literature.corpus import Corpus

logger = logging.getLogger("fulltext_assessment")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Assess full-text availability across the literature corpus."
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default=str(ROOT / "output" / "data" / "corpus.jsonl"),
        help="Path to the corpus JSONL file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT / "output" / "data"),
        help="Directory to write assessment JSON",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    return parser.parse_args()


def assess_corpus(corpus: Corpus) -> dict:
    """Assess full-text availability across the corpus.

    Args:
        corpus: Loaded Corpus object.

    Returns:
        Dictionary with assessment results.
    """
    papers = corpus.papers
    total = len(papers)

    # Abstract coverage
    has_abstract = sum(1 for p in papers if p.abstract and p.abstract.strip())
    no_abstract = total - has_abstract

    # Open access status
    oa_true = sum(1 for p in papers if p.is_open_access is True)
    oa_false = sum(1 for p in papers if p.is_open_access is False)
    oa_unknown = sum(1 for p in papers if p.is_open_access is None)

    # PDF URL availability
    has_pdf = sum(1 for p in papers if p.pdf_url)
    no_pdf = total - has_pdf

    # Full-text source breakdown
    source_counter: Counter = Counter()
    for p in papers:
        if p.full_text_source:
            source_counter[p.full_text_source] += 1
        else:
            source_counter["none"] += 1

    # PDF URL domain breakdown
    domain_counter: Counter = Counter()
    for p in papers:
        if p.pdf_url:
            # Extract domain from URL
            try:
                from urllib.parse import urlparse
                domain = urlparse(p.pdf_url).netloc
                domain_counter[domain] += 1
            except Exception:
                domain_counter["unknown"] += 1

    # ID coverage
    has_doi = sum(1 for p in papers if p.doi)
    has_arxiv = sum(1 for p in papers if p.arxiv_id)
    has_s2 = sum(1 for p in papers if p.s2_id)
    has_openalex = sum(1 for p in papers if p.openalex_id)

    # Full-text format assessment
    # Papers with arXiv IDs always have LaTeX source + PDF
    # Papers with publisher PDFs have PDF only
    format_breakdown = {
        "latex_source_and_pdf": sum(
            1 for p in papers if p.arxiv_id
        ),
        "publisher_pdf_only": sum(
            1 for p in papers
            if p.pdf_url and not p.arxiv_id
        ),
        "no_fulltext_available": sum(
            1 for p in papers if not p.pdf_url and not p.arxiv_id
        ),
    }

    pct = lambda n: round(100.0 * n / total, 1) if total > 0 else 0.0

    return {
        "total_papers": total,
        "abstract_coverage": {
            "has_abstract": has_abstract,
            "no_abstract": no_abstract,
            "percent_with_abstract": pct(has_abstract),
        },
        "open_access": {
            "is_oa": oa_true,
            "not_oa": oa_false,
            "unknown": oa_unknown,
            "percent_oa": pct(oa_true),
        },
        "pdf_availability": {
            "has_pdf_url": has_pdf,
            "no_pdf_url": no_pdf,
            "percent_with_pdf": pct(has_pdf),
        },
        "fulltext_source_breakdown": dict(
            source_counter.most_common()
        ),
        "pdf_domain_breakdown": dict(
            domain_counter.most_common(20)
        ),
        "identifier_coverage": {
            "doi": has_doi,
            "arxiv_id": has_arxiv,
            "s2_id": has_s2,
            "openalex_id": has_openalex,
        },
        "fulltext_format": format_breakdown,
    }


def main() -> None:
    """Run full-text assessment."""
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    corpus_path = Path(args.corpus)
    if not corpus_path.exists():
        logger.error("Corpus file not found: %s", corpus_path)
        sys.exit(1)

    logger.info("Loading corpus from %s", corpus_path)
    corpus = Corpus.load(corpus_path)
    logger.info("Loaded %d papers", len(corpus))

    results = assess_corpus(corpus)

    # Save results
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "fulltext_assessment.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    logger.info("Assessment saved to %s", output_path)

    # Print summary
    print("\n=== Full-Text Availability Assessment ===")
    print(f"Total papers: {results['total_papers']}")
    print(f"\nAbstract coverage: {results['abstract_coverage']['has_abstract']}/{results['total_papers']} "
          f"({results['abstract_coverage']['percent_with_abstract']}%)")
    print(f"\nOpen access: {results['open_access']['is_oa']}/{results['total_papers']} "
          f"({results['open_access']['percent_oa']}%)")
    print(f"  Not OA: {results['open_access']['not_oa']}")
    print(f"  Unknown: {results['open_access']['unknown']}")
    print(f"\nPDF availability: {results['pdf_availability']['has_pdf_url']}/{results['total_papers']} "
          f"({results['pdf_availability']['percent_with_pdf']}%)")
    print(f"\nFull-text source breakdown:")
    for source, count in results["fulltext_source_breakdown"].items():
        print(f"  {source}: {count}")
    print(f"\nFull-text format:")
    for fmt, count in results["fulltext_format"].items():
        pct = round(100.0 * count / results["total_papers"], 1) if results["total_papers"] > 0 else 0
        print(f"  {fmt}: {count} ({pct}%)")
    print(f"\nIdentifier coverage:")
    for id_type, count in results["identifier_coverage"].items():
        print(f"  {id_type}: {count}")
    print(f"\nTop PDF domains:")
    for domain, count in list(results["pdf_domain_breakdown"].items())[:10]:
        print(f"  {domain}: {count}")


if __name__ == "__main__":
    main()
