#!/usr/bin/env python3
"""Meta-analysis pipeline orchestrator.

Thin orchestrator that loads a corpus and runs all analysis modules:
text processing, citation network, temporal analysis, subfield
classification, and topic modeling. Includes reference normalization
to cross-match paper references against corpus canonical IDs for
building citation edges. All computation is imported from src/ modules;
this script handles only I/O and coordination.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Add src/ to path for project imports
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from literature.corpus import Corpus
from literature.models import Paper, Citation
from analysis.text_processing import build_tfidf_matrix
from analysis.citation_network import (
    build_citation_graph,
    compute_network_metrics,
    detect_communities,
    build_reference_index,
    resolve_citations,
)
from analysis.temporal_analysis import compute_temporal_metrics, estimate_growth_rate
from analysis.subfield_classifier import classify_corpus, SUBFIELDS
from analysis.topic_modeling import fit_nmf_topics, get_document_topics


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run meta-analysis pipeline on Active Inference corpus."
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default=str(ROOT / "output" / "data" / "corpus.jsonl"),
        help="Path to corpus JSONL file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT / "output"),
        help="Output directory for analysis results",
    )
    parser.add_argument(
        "--n-topics",
        type=int,
        default=5,
        help="Number of NMF topics to extract (default: 5)",
    )
    parser.add_argument(
        "--max-features",
        type=int,
        default=500,
        help="Maximum TF-IDF vocabulary size (default: 500)",
    )
    parser.add_argument(
        "--min-year",
        type=int,
        default=1960,
        help="Filter out papers before this year (default: 1960)",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for NMF reproducibility (default: 42)",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    return parser.parse_args()





def main() -> None:
    """Run the full meta-analysis pipeline."""
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("meta_analysis")

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    pipeline_start = time.monotonic()

    # Load corpus
    corpus_path = Path(args.corpus)
    logger.info("Loading corpus from: %s", corpus_path)
    corpus = Corpus.load(corpus_path)
    
    # Filter out anomalous early dates (configurable via --min-year)
    papers = [p for p in corpus.papers if p.year is None or p.year >= args.min_year]
    logger.info("Loaded %d papers (filtered >= %d)", len(papers), args.min_year)

    # 1. Subfield classification
    logger.info("--- Subfield Classification ---")
    t0 = time.monotonic()
    config_path = ROOT / "manuscript" / "config.yaml"
    classified = classify_corpus(papers, config_path=config_path)
    subfield_counts = {sf: len(plist) for sf, plist in classified.items()}
    logger.info("Subfield distribution: %s", subfield_counts)
    logger.info("Subfield classification completed in %.1fs", time.monotonic() - t0)

    subfield_path = data_dir / "subfield_classification.json"
    with open(subfield_path, "w", encoding="utf-8") as f:
        json.dump(subfield_counts, f, indent=2)
    print(str(subfield_path))

    # 1b. Per-subfield temporal breakdown (for subfield timeline figure)
    logger.info("--- Subfield Timeline ---")
    timeline: dict[str, dict[str, int]] = {}
    for sf, plist in classified.items():
        year_counts: dict[str, int] = {}
        for p in plist:
            if p.year:
                yr_key = str(p.year)
                year_counts[yr_key] = year_counts.get(yr_key, 0) + 1
        if year_counts:
            timeline[sf] = year_counts

    timeline_path = data_dir / "subfield_timeline.json"
    with open(timeline_path, "w", encoding="utf-8") as f:
        json.dump(timeline, f, indent=2)
    print(str(timeline_path))
    logger.info("Subfield timeline: %d subfields with temporal data", len(timeline))

    # 2. Temporal analysis
    logger.info("--- Temporal Analysis ---")
    t0 = time.monotonic()
    try:
        temporal = compute_temporal_metrics(papers)
        growth = estimate_growth_rate(temporal["year_counts"])

        temporal_results = {
            "year_counts": {str(k): v for k, v in temporal["year_counts"].items()},
            "smoothed_annual": {str(k): v for k, v in temporal.get("smoothed_annual", {}).items()},
            "cumulative": {str(k): v for k, v in temporal["cumulative"].items()},
            "first_year": temporal["first_year"],
            "last_year": temporal["last_year"],
            "total_papers": temporal["total_papers"],
            "peak_year": temporal["peak_year"],
            "mean_growth_rate": growth["mean_growth_rate"],
            "doubling_time": growth["doubling_time"],
            "cagr": growth["cagr"],
        }
        logger.info("Period: %d-%d", temporal['first_year'], temporal['last_year'])
        logger.info("Peak year: %d", temporal['peak_year'])
        logger.info("CAGR: %.2f%%", growth['cagr'] * 100)
        logger.info("Total papers with year: %d", temporal['total_papers'])
    except ValueError as e:
        logger.warning("Temporal analysis skipped: %s", e)
        temporal_results = {"error": str(e)}
    logger.info("Temporal analysis completed in %.1fs", time.monotonic() - t0)

    temporal_path = data_dir / "temporal_analysis.json"
    with open(temporal_path, "w", encoding="utf-8") as f:
        json.dump(temporal_results, f, indent=2)
    print(str(temporal_path))

    # 3. Text processing and TF-IDF
    logger.info("--- Text Processing ---")
    t0 = time.monotonic()

    # Build a per-paper subfield lookup for labeling TF-IDF rows
    paper_subfield: dict[str, str] = {}
    for sf, plist in classified.items():
        for p in plist:
            paper_subfield[p.canonical_id] = sf

    # Keep only papers with abstracts, in order
    papers_with_abs = [p for p in papers if p.abstract]
    documents = [p.abstract for p in papers_with_abs]
    doc_labels = [paper_subfield.get(p.canonical_id, "A2_philosophy") for p in papers_with_abs]
    if documents:
        tfidf_matrix, feature_names = build_tfidf_matrix(documents, max_features=args.max_features)
        logger.info(
            "TF-IDF matrix: %d docs x %d features (%.1fs)",
            tfidf_matrix.shape[0], tfidf_matrix.shape[1], time.monotonic() - t0,
        )

        # Tokenize docs for co-occurrence matrix
        from analysis.text_processing import tokenize, remove_stopwords
        doc_tokens = [remove_stopwords(tokenize(doc)) for doc in documents]

        # Persist TF-IDF data for figure generation
        tfidf_data = {
            "matrix": tfidf_matrix.tolist(),
            "feature_names": list(feature_names),
            "labels": doc_labels,
            "doc_tokens": doc_tokens,
        }
        tfidf_path = data_dir / "tfidf_data.json"
        with open(tfidf_path, "w", encoding="utf-8") as f:
            json.dump(tfidf_data, f)
        logger.info("TF-IDF data saved: %s (%.1f MB)", tfidf_path,
                    tfidf_path.stat().st_size / 1e6)
    else:
        logger.warning("No abstracts available for text processing")
        tfidf_matrix = None
        feature_names = []
        doc_labels = []

    # 4. Topic modeling
    logger.info("--- Topic Modeling ---")
    t0 = time.monotonic()
    if tfidf_matrix is not None and tfidf_matrix.size > 0:
        topics = fit_nmf_topics(tfidf_matrix, feature_names, n_topics=args.n_topics)
        for t in topics:
            logger.info("  Topic %d: %s", t['topic_id'], ', '.join(t['top_words'][:5]))
        logger.info("Topic modeling completed in %.1fs", time.monotonic() - t0)

        topics_path = data_dir / "topics.json"
        with open(topics_path, "w", encoding="utf-8") as f:
            json.dump(topics, f, indent=2)
        print(str(topics_path))
    else:
        logger.warning("Skipping topic modeling (no TF-IDF matrix)")

    # 5. Citation network with reference normalization
    logger.info("--- Citation Network ---")
    t0 = time.monotonic()

    # Build reference index for cross-matching
    logger.info("Building reference normalization index...")
    ref_index = build_reference_index(papers)
    logger.info("Reference index: %d entries from %d papers", len(ref_index), len(papers))

    # Resolve references to corpus citations
    citations = resolve_citations(papers, ref_index, logger)

    graph = build_citation_graph(papers, citations)
    metrics = compute_network_metrics(graph)
    logger.info("Network: %d nodes, %d edges", metrics['num_nodes'], metrics['num_edges'])
    logger.info("Density: %.4f", metrics['density'])
    logger.info("Components: %d", metrics['connected_components'])
    logger.info("Citation network completed in %.1fs", time.monotonic() - t0)

    communities = detect_communities(graph)

    # Annotate community assignments onto graph nodes
    for node_id, comm_id in communities.items():
        if graph.has_node(node_id):
            graph.nodes[node_id]["community"] = comm_id

    # Save full graph for visualization
    import networkx as nx
    gml_path = data_dir / "citation_graph.gml"
    nx.write_gml(graph, str(gml_path))
    logger.info("Citation graph saved: %s (%d nodes, %d edges)",
                gml_path, graph.number_of_nodes(), graph.number_of_edges())

    # Count total references across all papers for resolution rate
    total_refs = sum(
        len(p.references) if hasattr(p, 'references') and isinstance(p.references, list)
        else len(getattr(p, 'referenced_works', []) or [])
        for p in papers
    )

    network_results = {
        "num_nodes": metrics["num_nodes"],
        "num_edges": metrics["num_edges"],
        "density": metrics["density"],
        "avg_in_degree": metrics["avg_in_degree"],
        "connected_components": metrics["connected_components"],
        "num_communities": len(set(communities.values())) if communities else 0,
        "total_references": total_refs,
        "top_pagerank": {k: float(v) for k, v in list(metrics["pagerank"].items())[:5]},
        "top_hubs": {k: float(v) for k, v in list(metrics.get("hubs", {}).items())[:5]},
        "top_authorities": {k: float(v) for k, v in list(metrics.get("authorities", {}).items())[:5]},
    }

    network_path = data_dir / "citation_network.json"
    with open(network_path, "w", encoding="utf-8") as f:
        json.dump(network_results, f, indent=2)
    print(str(network_path))

    # Summary
    total_elapsed = time.monotonic() - pipeline_start
    logger.info("--- Pipeline Complete ---")
    logger.info("Papers analyzed: %d", len(papers))
    logger.info("Subfields: %d", sum(1 for v in subfield_counts.values() if v > 0))
    logger.info("Topics extracted: %d", args.n_topics)
    logger.info("Citation edges: %d", metrics['num_edges'])
    logger.info("Total pipeline time: %.1fs", total_elapsed)
    logger.info("Output directory: %s", output_dir)


if __name__ == "__main__":
    main()
