#!/usr/bin/env python3
"""Figure generation orchestrator.

Thin orchestrator that loads analysis results from JSON files and
calls visualization functions to generate all publication figures.
All rendering logic is imported from src/visualization/ modules;
this script handles only file I/O and coordination.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path

# Force headless matplotlib backend
os.environ["MPLBACKEND"] = "Agg"

# Add repo root and src/ to path for imports
ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = ROOT.parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(REPO_ROOT))
sys.path.insert(0, str(SRC))

from infrastructure.documentation.figure_manager import FigureManager

from visualization.field_overview import plot_field_summary, plot_subfield_distribution
from visualization.citation_plots import plot_citation_network, plot_degree_distribution
from visualization.temporal_plots import plot_growth_curve, plot_subfield_timeline
from visualization.style import apply_visual_style
from visualization.hypothesis_charts import (
    plot_hypothesis_dashboard,
    plot_evidence_timeline,
    plot_assertion_type_breakdown,
    plot_assertion_summary,
)
from visualization.advanced_plots import (
    plot_word_cloud,
    plot_pca_embeddings,
    plot_term_heatmap,
    plot_dendrogram,
    plot_topic_term_bars,
    plot_cooccurrence_matrix,
)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Generate all figures for the Active Inference meta-analysis."
    )
    parser.add_argument(
        "--input-dir",
        type=str,
        default=str(ROOT / "output" / "data"),
        help="Directory containing analysis JSON results",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT / "output" / "figures"),
        help="Directory to save generated figures",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Output figure DPI (default: 300)",
    )
    return parser.parse_args()


def _load_json(path: Path) -> dict:
    """Load a JSON file, returning empty dict if not found."""
    _log = logging.getLogger("generate_figures")
    if not path.exists():
        _log.warning(f"  {path} not found, skipping")
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def main() -> None:
    """Generate all figures from analysis results."""
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("generate_figures")

    import matplotlib
    matplotlib.rcParams["savefig.dpi"] = args.dpi
    apply_visual_style()

    input_dir = Path(args.input_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    generated_paths: list[str] = []

    # 1. Field overview figures
    logger.info("--- Field Overview Figures ---")
    subfield_data = _load_json(input_dir / "subfield_classification.json")
    if subfield_data:
        total_papers = sum(subfield_data.values())

        path = plot_field_summary(total_papers, subfield_data,
                                  output_dir / "field_summary.png")
        generated_paths.append(str(path))
        print(f"  Generated: {path}")

        path = plot_subfield_distribution(subfield_data,
                                          output_dir / "subfield_distribution.png")
        generated_paths.append(str(path))
        logger.info(f"  Generated: {path}")

    # 2. Temporal figures
    logger.info("--- Temporal Figures ---")
    temporal_data = _load_json(input_dir / "temporal_analysis.json")
    if temporal_data and "year_counts" in temporal_data:
        year_counts = {int(k): v for k, v in temporal_data["year_counts"].items()}
        cumulative = {int(k): v for k, v in temporal_data["cumulative"].items()}
        smoothed_annual = {int(k): v for k, v in temporal_data.get("smoothed_annual", {}).items()}

        path = plot_growth_curve(year_counts, cumulative,
                                 output_dir / "growth_curve.png",
                                 smoothed_annual=smoothed_annual)
        generated_paths.append(str(path))
        logger.info(f"  Generated: {path}")

    # Build subfield timeline from per-subfield temporal data if available
    subfield_timeline_data = _load_json(input_dir / "subfield_timeline.json")
    if subfield_timeline_data:
        converted = {
            sf: {int(k): v for k, v in yrs.items()}
            for sf, yrs in subfield_timeline_data.items()
        }
        path = plot_subfield_timeline(converted,
                                      output_dir / "subfield_timeline.png")
        generated_paths.append(str(path))
        logger.info(f"  Generated: {path}")

    # 3. Citation network figures
    logger.info("--- Citation Network Figures ---")
    network_data = _load_json(input_dir / "citation_network.json")
    if network_data and network_data.get("num_nodes", 0) > 0:
        # Reconstruct graph from saved GML or build a representative
        # subgraph from the top-PageRank nodes in the metrics JSON
        try:
            import networkx as nx
            # Try to load serialized graph
            graph_path = input_dir / "citation_graph.gml"
            if graph_path.exists():
                graph = nx.read_gml(graph_path)
            else:
                # Create a small representative graph from metrics
                graph = nx.DiGraph()
                for node_id in list(network_data.get("top_pagerank", {}).keys()):
                    graph.add_node(node_id)
                logger.info("  Using top PageRank nodes for network visualization")

            if graph.number_of_nodes() > 0:
                path = plot_citation_network(graph,
                                             output_dir / "citation_network.png")
                generated_paths.append(str(path))
                logger.info(f"  Generated: {path}")

                path = plot_degree_distribution(graph,
                                                output_dir / "degree_distribution.png")
                generated_paths.append(str(path))
                logger.info(f"  Generated: {path}")
        except Exception as e:
            logger.error(f"  Citation network figures skipped: {e}")

    # 4. Hypothesis figures
    logger.info("--- Hypothesis Figures ---")
    scores_data = _load_json(input_dir / "hypothesis_scores.json")
    if scores_data:
        path = plot_hypothesis_dashboard(scores_data,
                                         output_dir / "hypothesis_dashboard.png")
        generated_paths.append(str(path))
        logger.info(f"  Generated: {path}")

    trends_data = _load_json(input_dir / "hypothesis_trends.json")
    if trends_data:
        converted_trends = {
            hyp: {int(k): v for k, v in yrs.items()}
            for hyp, yrs in trends_data.items()
        }
        path = plot_evidence_timeline(converted_trends,
                                      output_dir / "evidence_timeline.png")
        generated_paths.append(str(path))
        logger.info(f"  Generated: {path}")

    # 5. Advanced figures (word cloud, PCA, heatmap, dendrogram, topics, co-occ)
    logger.info("--- Advanced Figures ---")
    topics_data = _load_json(input_dir / "topics.json")

    # Word cloud from topic top-words
    if topics_data and isinstance(topics_data, list):
        word_weights: dict[str, float] = {}
        for topic in topics_data:
            for word, weight in zip(
                topic.get("top_words", []), topic.get("weights", [])
            ):
                word_weights[word] = max(word_weights.get(word, 0), weight)
        if word_weights:
            path = plot_word_cloud(word_weights, output_dir / "word_cloud.png")
            generated_paths.append(str(path))
            logger.info(f"  Generated: {path}")

        # Topic-term bars
        path = plot_topic_term_bars(topics_data, output_dir / "topic_term_bars.png")
        generated_paths.append(str(path))
        logger.info(f"  Generated: {path}")

    # TF-IDF-based figures: PCA, heatmap, dendrogram, co-occurrence
    tfidf_data = _load_json(input_dir / "tfidf_data.json")
    if tfidf_data and "matrix" in tfidf_data:
        import numpy as np
        tfidf_matrix = np.array(tfidf_data["matrix"], dtype=np.float64)
        feature_names = tfidf_data.get("feature_names", [])
        doc_labels = tfidf_data.get("labels", [])
        doc_tokens = tfidf_data.get("doc_tokens", [])

        if tfidf_matrix.shape[0] >= 2 and doc_labels:
            path = plot_pca_embeddings(
                tfidf_matrix, doc_labels, feature_names,
                output_dir / "pca_embeddings.png",
            )
            generated_paths.append(str(path))
            logger.info(f"  Generated: {path}")

            path = plot_term_heatmap(
                tfidf_matrix, feature_names, doc_labels,
                output_dir / "term_heatmap.png",
            )
            generated_paths.append(str(path))
            logger.info(f"  Generated: {path}")

            path = plot_dendrogram(
                tfidf_matrix, doc_labels,
                output_dir / "dendrogram.png",
            )
            generated_paths.append(str(path))
            logger.info(f"  Generated: {path}")

        if doc_tokens:
            path = plot_cooccurrence_matrix(
                doc_tokens,
                output_dir / "cooccurrence_matrix.png",
            )
            generated_paths.append(str(path))
            logger.info(f"  Generated: {path}")

    # 6. Assertion / nanopublication figures
    logger.info("--- Assertion Figures ---")
    assertion_data = _load_json(input_dir / "assertion_summary.json")
    if assertion_data:
        # Assertion type breakdown per hypothesis
        per_hyp = assertion_data.get("per_hypothesis", {})
        if per_hyp:
            path = plot_assertion_type_breakdown(
                per_hyp, output_dir / "assertion_breakdown.png"
            )
            generated_paths.append(str(path))
            logger.info(f"  Generated: {path}")

        # Assertion summary panel
        total = assertion_data.get("total_assertions", 0)
        type_counts = assertion_data.get("type_counts", {})
        hyp_totals = {
            h: sum(v.values()) for h, v in per_hyp.items()
        } if per_hyp else {}
        if total > 0:
            path = plot_assertion_summary(
                total, type_counts, hyp_totals,
                output_dir / "assertion_summary.png",
            )
            generated_paths.append(str(path))
            logger.info(f"  Generated: {path}")

    # Print all generated paths for manifest collection
    logger.info(f"--- Summary: {len(generated_paths)} figures generated ---")
    for p in generated_paths:
        print(p)

    # Register figures in figure_registry.json
    logger.info("--- Registering Figures ---")
    registry_file = output_dir / "figure_registry.json"
    figure_manager = FigureManager(str(registry_file))
    
    # Pre-defined mapping for descriptive captions
    captions = {
        "field_summary.png": "High-level overview of retrieved literature and subfield counts.",
        "subfield_distribution.png": "Distribution of distinct subfields identified in the literature.",
        "growth_curve.png": "Annual and cumulative growth of publications over time.",
        "subfield_timeline.png": "Temporal evolution of publications by subfield.",
        "citation_network.png": "Citation network demonstrating connections between top papers.",
        "degree_distribution.png": "Degree distribution of nodes within the citation network.",
        "hypothesis_dashboard.png": "Dashboard showing evidence scores for proposed hypotheses.",
        "evidence_timeline.png": "Timeline of evidence score accumulation for each hypothesis.",
        "word_cloud.png": "Word cloud of salient terms appearing in abstract text.",
        "topic_term_bars.png": "Top terms and corresponding weights per discovered topic.",
        "pca_embeddings.png": "PCA plot of TF-IDF vectors highlighting document clusters.",
        "term_heatmap.png": "Heatmap of dominant TF-IDF terms across analyzed documents.",
        "dendrogram.png": "Hierarchical clustering dendrogram showing document similarity.",
        "cooccurrence_matrix.png": "Co-occurrence matrix for significant terms.",
        "assertion_breakdown.png": "Breakdown of nanopublication assertion types by hypothesis.",
        "assertion_summary.png": "Summary of total extracted nanopublication assertions."
    }

    for path_str in generated_paths:
        path = Path(path_str)
        filename = path.name
        caption = captions.get(filename, f"Figure showing {filename.replace('.png', '').replace('_', ' ')}.")
        label = f"fig:{path.stem}"
        
        # Check if already registered to avoid duplicates if script is run multiple times
        if not figure_manager.get_figure(label):
            figure_manager.register_figure(
                filename=filename,
                caption=caption,
                label=label,
                generated_by="04_generate_figures.py"
            )
            logger.info(f"  Registered {filename} -> {label}")
        else:
            logger.info(f"  Figure {label} already registered.")


if __name__ == "__main__":
    main()
