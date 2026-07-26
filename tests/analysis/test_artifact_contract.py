"""Tests for the cross-stage artifact contract."""

from __future__ import annotations

import json
from pathlib import Path

import networkx as nx

from analysis.artifact_contract import validate_artifacts
from knowledge_graph.nanopublication import (
    Assertion,
    create_nanopub,
    serialize_nanopubs,
    serialize_nanopubs_to_trig,
)
from knowledge_graph.provenance import ExtractionProvenance, write_provenance_summary
from literature.corpus import Corpus
from literature.models import Paper


def test_validate_complete_artifact_fixture(tmp_path: Path) -> None:
    project = tmp_path
    output = project / "output"
    data = output / "data"
    figures = output / "figures"
    manuscript = output / "manuscript"
    reports = output / "reports"
    for directory in (data, figures, manuscript, reports, project / "manuscript"):
        directory.mkdir(parents=True)

    (project / "manuscript" / "config.yaml").write_text(
        "analysis:\n  n_topics: 2\n  topic_stability_seeds: [42, 43]\n",
        encoding="utf-8",
    )
    figure_labels = "\n".join(f"fig:figure_{index}" for index in range(16))
    (project / "manuscript" / "00_abstract.md").write_text(
        "Corpus {{CORPUS_SIZE}}\n" + figure_labels, encoding="utf-8"
    )
    corpus = Corpus()
    corpus.add(Paper("Test paper", "active inference abstract", year=2024, doi="10.1/test"))
    corpus.save(data / "corpus.jsonl")
    (data / "subfield_classification.json").write_text(
        json.dumps({"A1_formal": 1, "A2_philosophy": 0, "B_tools": 0, "C1_neuroscience": 0,
                    "C2_robotics": 0, "C3_language": 0, "C4_psychiatry": 0, "C5_biology": 0}),
        encoding="utf-8",
    )
    (data / "temporal_analysis.json").write_text(
        json.dumps({"year_counts": {"2024": 1}, "total_papers": 1,
                    "first_year": 2024, "last_year": 2024,
                    "current_year_is_partial": False, "cagr_end_year": 2024,
                    "current_year": 2024}), encoding="utf-8"
    )
    (data / "tfidf_data.json").write_text(
        json.dumps({"matrix": [[1.0]], "feature_names": ["term"],
                    "labels": ["A1_formal"], "doc_tokens": [["term"]]}), encoding="utf-8"
    )
    (data / "topics.json").write_text(
        json.dumps([{"topic_id": 0, "top_words": ["term"], "weights": [1.0]},
                    {"topic_id": 1, "top_words": ["other"], "weights": [1.0]}]), encoding="utf-8"
    )
    (data / "topic_stability.json").write_text(
        json.dumps({
            "n_topics": 2,
            "seeds": [42, 43],
            "primary_seed": 42,
            "pairwise_comparisons": [{"seed_a": 42, "seed_b": 43, "mean_jaccard": 1.0}],
            "mean_jaccard": 1.0,
            "min_jaccard": 1.0,
        }), encoding="utf-8"
    )
    graph = nx.DiGraph()
    graph.add_node("doi:10.1/test")
    nx.write_gml(graph, data / "citation_graph.gml")
    (data / "citation_network.json").write_text(
        json.dumps({"num_nodes": 1, "num_edges": 0}), encoding="utf-8"
    )

    assertion = Assertion("a1", "doi:10.1/test", "claim", "supports", "FEP_UNIVERSALITY", 0.9, 1)
    provenance = ExtractionProvenance.create(
        paper_id="doi:10.1/test", source_passage="abstract",
        model_id="gemma3:4b", llm_url="http://localhost:11434",
        pipeline_version="fixture-pipeline", prompt_version="fixture-prompt", run_id="run1"
    ).to_dict()
    nanopub = create_nanopub(assertion, attribution="test", provenance=provenance)
    serialize_nanopubs([nanopub], data / "nanopublications.jsonl")
    serialize_nanopubs_to_trig([nanopub], data / "nanopublications.trig")
    write_provenance_summary(data / "nanopublications.jsonl",
                             reports / "extraction_provenance_summary.json")
    (data / "assertion_summary.json").write_text(
        json.dumps({"total_assertions": 1, "type_counts": {"supports": 1},
                    "per_hypothesis": {"FEP_UNIVERSALITY": {"supports": 1}}}), encoding="utf-8"
    )
    fixture_scores = {key: 0.0 for key in (
        "FEP_UNIVERSALITY", "AIF_OPTIMALITY", "MARKOV_BLANKET_REALISM", "PREDICTIVE_CODING",
        "SCALABILITY", "CLINICAL_UTILITY", "MORPHOGENESIS", "LANGUAGE_AIF")}
    fixture_scores["FEP_UNIVERSALITY"] = 1.0
    (data / "hypothesis_scores.json").write_text(json.dumps(fixture_scores), encoding="utf-8")
    for name, payload in {
        "hypothesis_trends.json": {}, "hypothesis_sensitivity.json": {},
        "fulltext_assessment.json": {
            "total_papers": 1,
            "abstract_coverage": {"has_abstract": 1, "no_abstract": 0},
            "open_access": {"is_oa": 0, "not_oa": 1, "unknown": 0},
            "pdf_availability": {"has_pdf_url": 0, "no_pdf_url": 1},
            "fulltext_source_breakdown": {"none": 1},
            "fulltext_format": {"no_fulltext_available": 1},
        },
        "validation_metrics.json": {"sample_size": 1},
        "extraction_coverage.json": {"total_papers": 1, "eligible_papers": 1, "processed_papers": 1,
                                      "failed_papers": 0, "unprocessed_papers": 0,
                                      "assertions": 1,
                                      "run_id": "run1", "model_id": "gemma3:4b",
                                      "prompt_version": "fixture-prompt", "pipeline_version": "fixture-pipeline"},
        "extraction_state.json": {"status": "complete", "run_id": "run1",
                                   "model_id": "gemma3:4b", "prompt_version": "fixture-prompt",
                                   "pipeline_version": "fixture-pipeline"},
    }.items():
        (data / name).write_text(json.dumps(payload), encoding="utf-8")

    (reports / "search_provenance.json").write_text(json.dumps({
        "requested_sources": ["arxiv", "semantic_scholar", "openalex"],
        "latest_source_status": {
            "arXiv[1]": {"success": True},
            "Semantic Scholar": {"success": True},
            "OpenAlex": {"success": True},
        },
    }), encoding="utf-8")

    registry = {}
    for index in range(16):
        filename = f"figure_{index}.png"
        (figures / filename).write_bytes(b"png")
        registry[f"fig:figure_{index}"] = {"filename": filename}
    (figures / "figure_registry.json").write_text(json.dumps(registry), encoding="utf-8")
    (manuscript / "00_abstract.md").write_text("Corpus 1\n" + figure_labels, encoding="utf-8")
    (data / "manuscript_variables.json").write_text(
        json.dumps({"source_tokens": {"CORPUS_SIZE": ["00_abstract.md"]},
                    "variables": {"CORPUS_SIZE": "1"}}), encoding="utf-8"
    )

    report = validate_artifacts(output, project)
    assert report["status"] == "pass", report["errors"]

    # Adversarial controls cover the fail-closed source and stability gates.
    search_path = reports / "search_provenance.json"
    search = json.loads(search_path.read_text(encoding="utf-8"))
    search["latest_source_status"]["arXiv[1]"]["success"] = False
    search_path.write_text(json.dumps(search), encoding="utf-8")
    incomplete_path = data / "topic_stability.json"
    incomplete = json.loads(incomplete_path.read_text(encoding="utf-8"))
    incomplete["pairwise_comparisons"] = []
    incomplete_path.write_text(json.dumps(incomplete), encoding="utf-8")
    fulltext_path = data / "fulltext_assessment.json"
    fulltext = json.loads(fulltext_path.read_text(encoding="utf-8"))
    fulltext["total_papers"] = 2
    fulltext["abstract_coverage"]["has_abstract"] = 0
    fulltext["fulltext_source_breakdown"]["none"] = 0
    fulltext_path.write_text(json.dumps(fulltext), encoding="utf-8")
    adversarial = validate_artifacts(output, project)
    assert any("arxiv" in error for error in adversarial["errors"])
    assert any("pairwise comparison count" in error for error in adversarial["errors"])
    assert any("full-text assessment total" in error for error in adversarial["errors"])
    assert any("full-text abstract_coverage" in error for error in adversarial["errors"])
    assert any("full-text fulltext_source_breakdown" in error for error in adversarial["errors"])
