"""Meta-analysis pipeline: bibliometrics, text, citation network."""

from __future__ import annotations

import argparse
import json
import logging
import time
from datetime import date
from pathlib import Path

import networkx as nx

from analysis.citation_network import (
    build_citation_graph,
    build_reference_index,
    compute_network_metrics,
    detect_communities,
    resolve_citations,
)
from analysis.subfield_classifier import classify_corpus
from analysis.temporal_analysis import (
    compute_subfield_timeline,
    compute_temporal_metrics,
    estimate_growth_rate,
)
from analysis.text_processing import build_tfidf_matrix, tokenize_documents
from analysis.topic_modeling import fit_nmf_topics
from analysis.topic_stability import compute_topic_stability
from config_loader import load_analysis_config
from literature.corpus import Corpus
from literature.models import Paper


def _count_paper_references(paper: Paper) -> int:
    refs = getattr(paper, "references", None)
    if isinstance(refs, list) and refs:
        return len(refs)
    return 0


def run_meta_analysis_pipeline(args: argparse.Namespace, *, project_root: Path) -> None:
    """Run bibliometric analysis and write JSON artifacts under output/data/."""
    logger = logging.getLogger("meta_analysis")
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    pipeline_start = time.monotonic()

    config_path = project_root / "manuscript" / "config.yaml"
    analysis_cfg = load_analysis_config(config_path)
    args.n_topics = analysis_cfg["n_topics"]
    args.max_features = analysis_cfg["max_features"]
    args.min_year = analysis_cfg["min_year"]
    args.seed = analysis_cfg["seed"]

    corpus = Corpus.load(Path(args.corpus))
    papers = [p for p in corpus.papers if p.year is None or p.year >= args.min_year]
    logger.info("Loaded %d papers (filtered >= %d)", len(papers), args.min_year)

    config_path = project_root / "manuscript" / "config.yaml"
    classified = classify_corpus(papers, config_path=config_path)
    subfield_counts = {sf: len(plist) for sf, plist in classified.items()}
    subfield_path = data_dir / "subfield_classification.json"
    with open(subfield_path, "w", encoding="utf-8") as handle:
        json.dump(subfield_counts, handle, indent=2)
    print(str(subfield_path))

    timeline = compute_subfield_timeline(classified)
    timeline_path = data_dir / "subfield_timeline.json"
    with open(timeline_path, "w", encoding="utf-8") as handle:
        json.dump(timeline, handle, indent=2)
    print(str(timeline_path))

    try:
        temporal = compute_temporal_metrics(papers)
        configured_as_of_date = analysis_cfg.get("as_of_date")
        as_of_date = (
            date.fromisoformat(str(configured_as_of_date))
            if configured_as_of_date
            else date.today()
        )
        observed_last_year = temporal["last_year"]
        current_year_is_partial = observed_last_year == as_of_date.year
        cagr_end_year = (
            as_of_date.year - 1 if current_year_is_partial else observed_last_year
        )
        growth = estimate_growth_rate(
            temporal["year_counts"],
            end_year=cagr_end_year,
        )
        temporal_results = {
            "year_counts": {str(k): v for k, v in temporal["year_counts"].items()},
            "smoothed_annual": {
                str(k): v for k, v in temporal.get("smoothed_annual", {}).items()
            },
            "cumulative": {str(k): v for k, v in temporal["cumulative"].items()},
            "first_year": temporal["first_year"],
            "last_year": temporal["last_year"],
            "total_papers": temporal["total_papers"],
            "corpus_size": len(papers),
            "undated_papers": len(papers) - temporal["total_papers"],
            "peak_year": temporal["peak_year"],
            "mean_growth_rate": growth["mean_growth_rate"],
            "doubling_time": growth["doubling_time"],
            "cagr": growth["cagr"],
            "as_of_date": as_of_date.isoformat(),
            "current_year": as_of_date.year,
            "current_year_is_partial": current_year_is_partial,
            "current_year_papers": temporal["year_counts"].get(as_of_date.year, 0),
            "cagr_start_year": growth["cagr_start_year"],
            "cagr_end_year": growth["cagr_end_year"],
            "cagr_excludes_partial_year": current_year_is_partial,
            "complete_year_policy": analysis_cfg["complete_year_policy"],
        }
    except ValueError as exc:
        logger.warning("Temporal analysis skipped: %s", exc)
        temporal_results = {"error": str(exc)}

    temporal_path = data_dir / "temporal_analysis.json"
    with open(temporal_path, "w", encoding="utf-8") as handle:
        json.dump(temporal_results, handle, indent=2)
    print(str(temporal_path))

    paper_subfield = {
        paper.canonical_id: sf
        for sf, plist in classified.items()
        for paper in plist
    }
    papers_with_abs = [p for p in papers if p.abstract]
    documents = [p.abstract for p in papers_with_abs]
    doc_labels = [
        paper_subfield.get(p.canonical_id, "A2_philosophy") for p in papers_with_abs
    ]

    tfidf_matrix = None
    feature_names: list[str] = []
    if documents:
        tfidf_matrix, feature_names = build_tfidf_matrix(
            documents, max_features=args.max_features
        )
        tfidf_data = {
            "matrix": tfidf_matrix.tolist(),
            "feature_names": list(feature_names),
            "labels": doc_labels,
            "doc_tokens": tokenize_documents(documents),
        }
        tfidf_path = data_dir / "tfidf_data.json"
        with open(tfidf_path, "w", encoding="utf-8") as handle:
            json.dump(tfidf_data, handle)
        logger.info("TF-IDF data saved: %s", tfidf_path)

    if tfidf_matrix is not None and tfidf_matrix.size > 0:
        topics = fit_nmf_topics(tfidf_matrix, feature_names, n_topics=args.n_topics)
        topics_path = data_dir / "topics.json"
        with open(topics_path, "w", encoding="utf-8") as handle:
            json.dump(topics, handle, indent=2)
        print(str(topics_path))

        stability = compute_topic_stability(
            tfidf_matrix,
            feature_names,
            n_topics=args.n_topics,
            seeds=analysis_cfg["topic_stability_seeds"],
        )
        stability_path = data_dir / "topic_stability.json"
        with open(stability_path, "w", encoding="utf-8") as handle:
            json.dump(stability, handle, indent=2)
        print(str(stability_path))

    ref_index = build_reference_index(papers)
    citations = resolve_citations(papers, ref_index, logger)
    graph = build_citation_graph(papers, citations)
    metrics = compute_network_metrics(graph)
    communities = detect_communities(graph)
    for node_id, comm_id in communities.items():
        if graph.has_node(node_id):
            graph.nodes[node_id]["community"] = comm_id

    gml_path = data_dir / "citation_graph.gml"
    nx.write_gml(graph, str(gml_path))

    view_limit = 100
    view_nodes = sorted(
        graph.in_degree(), key=lambda item: (-item[1], str(item[0]))
    )[:view_limit]
    view_node_ids = {node_id for node_id, _degree in view_nodes}
    view_edges = graph.subgraph(view_node_ids).number_of_edges()

    network_results = {
        "num_nodes": metrics["num_nodes"],
        "num_edges": metrics["num_edges"],
        "density": metrics["density"],
        "avg_in_degree": metrics["avg_in_degree"],
        "avg_out_degree": metrics["avg_out_degree"],
        "max_in_degree": metrics["max_in_degree"],
        "max_out_degree": metrics["max_out_degree"],
        "connected_components": metrics["connected_components"],
        "num_communities": len(set(communities.values())) if communities else 0,
        "total_references": sum(_count_paper_references(p) for p in papers),
        "figure_view_nodes": min(view_limit, graph.number_of_nodes()),
        "figure_view_edges": view_edges,
        "top_pagerank": {k: float(v) for k, v in list(metrics["pagerank"].items())[:5]},
        "top_hubs": {k: float(v) for k, v in list(metrics.get("hubs", {}).items())[:5]},
        "top_authorities": {
            k: float(v) for k, v in list(metrics.get("authorities", {}).items())[:5]
        },
    }
    network_path = data_dir / "citation_network.json"
    with open(network_path, "w", encoding="utf-8") as handle:
        json.dump(network_results, handle, indent=2)
    print(str(network_path))

    logger.info(
        "Pipeline complete in %.1fs (%d papers, %d citation edges)",
        time.monotonic() - pipeline_start,
        len(papers),
        metrics["num_edges"],
    )
