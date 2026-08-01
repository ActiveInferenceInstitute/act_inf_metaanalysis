"""Cross-artifact validation for the publication package."""

from __future__ import annotations

import json
import hashlib
import re
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any

import networkx as nx

from config_loader import load_analysis_config
from knowledge_graph.hypothesis import score_hypothesis
from knowledge_graph.nanopublication import deserialize_nanopubs
from knowledge_graph.provenance import summarize_provenance
from literature.models import Paper
from manuscript.variables import TOKEN_RE, collect_manuscript_tokens, compute_variables
from analysis.release_package import validate_rdf_package


def _load(path: Path) -> Any:
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def _file_metadata(path: Path) -> dict[str, int | str]:
    """Return the metadata format used by manuscript and pipeline manifests."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return {"sha256": digest.hexdigest(), "size_bytes": path.stat().st_size}


def validate_artifacts(output_dir: Path, project_root: Path) -> dict[str, Any]:
    """Validate the regenerated data, figures, provenance, and hydration chain."""
    data_dir = output_dir / "data"
    errors: list[str] = []
    warnings: list[str] = []

    required = [
        "corpus.jsonl",
        "subfield_classification.json",
        "temporal_analysis.json",
        "tfidf_data.json",
        "topics.json",
        "topic_stability.json",
        "citation_network.json",
        "citation_graph.gml",
        "nanopublications.jsonl",
        "nanopublications.trig",
        "hypothesis_scores.json",
        "hypothesis_trends.json",
        "assertion_summary.json",
        "hypothesis_sensitivity.json",
        "fulltext_assessment.json",
        "validation_metrics.json",
        "extraction_coverage.json",
        "extraction_state.json",
        "manuscript_variables.json",
    ]
    for name in required:
        if not (data_dir / name).exists():
            errors.append(f"missing data artifact: {name}")

    coverage_path = data_dir / "extraction_coverage.json"
    coverage = _load(coverage_path) if coverage_path.exists() else {}
    required_coverage_fields = (
        "total_papers",
        "eligible_papers",
        "processed_papers",
        "failed_papers",
        "unprocessed_papers",
        "assertions",
        "model_id",
        "prompt_version",
        "pipeline_version",
        "run_id",
    )
    for field in required_coverage_fields:
        if field not in coverage or coverage.get(field) in (None, ""):
            errors.append(f"extraction coverage is missing {field}")

    search_report_path = output_dir / "reports" / "search_provenance.json"
    if not search_report_path.exists():
        errors.append("missing report artifact: search_provenance.json")
    else:
        search_report = _load(search_report_path)
        latest = search_report.get("latest_source_status", {})
        arxiv_events = [
            event for name, event in latest.items()
            if str(name).lower().startswith("arxiv[")
        ]
        source_checks = {
            "arxiv": bool(arxiv_events) and all(
                bool(event.get("success")) for event in arxiv_events
            ),
            "semantic_scholar": bool(latest.get("Semantic Scholar", {}).get("success")),
            "openalex": bool(latest.get("OpenAlex", {}).get("success")),
        }
        for source in search_report.get("requested_sources", []):
            if source in source_checks and not source_checks[source]:
                errors.append(f"literature source did not complete successfully: {source}")
            elif source not in source_checks:
                errors.append(f"literature source has no validator mapping: {source}")

    corpus_rows = []
    corpus_path = data_dir / "corpus.jsonl"
    if corpus_path.exists():
        for line_number, line in enumerate(corpus_path.read_text(encoding="utf-8").splitlines(), 1):
            if not line.strip():
                continue
            try:
                corpus_rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                errors.append(f"invalid corpus JSONL line {line_number}: {exc}")

    paper_years: dict[str, int | None] = {}
    corpus_reference_count = 0
    for row in corpus_rows:
        try:
            paper = Paper.from_dict(row)
            paper_years[paper.canonical_id] = paper.year
            corpus_reference_count += len(paper.references or [])
        except (KeyError, TypeError, ValueError) as exc:
            errors.append(f"invalid corpus record: {exc}")

    if coverage:
        if coverage.get("total_papers") != len(corpus_rows):
            errors.append("extraction coverage total does not equal corpus size")
        eligible = int(coverage.get("eligible_papers", 0))
        processed = int(coverage.get("processed_papers", 0))
        failed = int(coverage.get("failed_papers", 0))
        unprocessed = int(coverage.get("unprocessed_papers", 0))
        if eligible < 0 or eligible > len(corpus_rows):
            errors.append("extraction eligible-paper count is outside corpus bounds")
        if processed + failed + unprocessed != eligible:
            errors.append("extraction coverage statuses do not equal eligible papers")

    if corpus_rows and (data_dir / "subfield_classification.json").exists():
        subfields = _load(data_dir / "subfield_classification.json")
        if sum(subfields.values()) != len(corpus_rows):
            errors.append("subfield totals do not equal corpus size")

    if (data_dir / "temporal_analysis.json").exists():
        temporal = _load(data_dir / "temporal_analysis.json")
        year_counts = {int(year): count for year, count in temporal.get("year_counts", {}).items()}
        if sum(year_counts.values()) != temporal.get("total_papers"):
            errors.append("temporal year counts do not equal temporal total")
        temporal_total = int(temporal.get("total_papers", 0))
        undated = int(
            temporal.get("undated_papers", max(len(corpus_rows) - temporal_total, 0))
        )
        if temporal_total + undated != len(corpus_rows):
            errors.append("temporal dated plus undated totals do not equal corpus size")
        if "current_year_papers" in temporal:
            current_year = str(temporal.get("current_year"))
            if int(temporal.get("current_year_papers", 0)) != int(
                temporal.get("year_counts", {}).get(current_year, 0)
            ):
                errors.append("temporal current-year count disagrees with year counts")
        if temporal.get("current_year_is_partial") and temporal.get("cagr_end_year") >= temporal.get("current_year"):
            errors.append("partial current year was included in CAGR endpoint")
        analysis_config = load_analysis_config(project_root / "manuscript" / "config.yaml")
        configured_as_of = analysis_config.get("as_of_date")
        if configured_as_of and temporal.get("as_of_date") != configured_as_of:
            errors.append("temporal as_of_date differs from configuration")
        if configured_as_of and temporal.get("current_year") != int(str(configured_as_of)[:4]):
            errors.append("temporal current year differs from configured as_of_date")
        if (
            "complete_year_policy" in temporal
            and temporal.get("complete_year_policy")
            != analysis_config.get("complete_year_policy")
        ):
            errors.append("temporal complete-year policy differs from configuration")

    fulltext_path = data_dir / "fulltext_assessment.json"
    if fulltext_path.exists() and corpus_rows:
        fulltext = _load(fulltext_path)
        if fulltext.get("total_papers") != len(corpus_rows):
            errors.append("full-text assessment total does not equal corpus size")
        coverage_groups = {
            "abstract_coverage": ("has_abstract", "no_abstract"),
            "open_access": ("is_oa", "not_oa", "unknown"),
            "pdf_availability": ("has_pdf_url", "no_pdf_url"),
        }
        for group, fields in coverage_groups.items():
            values = fulltext.get(group, {})
            if sum(int(values.get(field, 0)) for field in fields) != len(corpus_rows):
                errors.append(f"full-text {group} counts do not equal corpus size")
        for group in ("fulltext_source_breakdown", "fulltext_format"):
            values = fulltext.get(group, {})
            if sum(int(count) for count in values.values()) != len(corpus_rows):
                errors.append(f"full-text {group} totals do not equal corpus size")

    if (data_dir / "citation_network.json").exists() and corpus_rows:
        citation = _load(data_dir / "citation_network.json")
        if citation.get("num_nodes") != len(corpus_rows):
            errors.append("citation node count does not equal corpus size")
        if "total_references" in citation and citation.get("total_references") != corpus_reference_count:
            errors.append("citation total references do not equal corpus references")
        graph_path = data_dir / "citation_graph.gml"
        if graph_path.exists():
            try:
                graph = nx.read_gml(graph_path)
                if graph.number_of_nodes() != citation.get("num_nodes"):
                    errors.append("citation graph nodes disagree with citation metrics")
                if graph.number_of_edges() != citation.get("num_edges"):
                    errors.append("citation graph edges disagree with citation metrics")
                view_nodes = int(citation.get("figure_view_nodes", min(100, graph.number_of_nodes())))
                top_nodes = sorted(
                    graph.in_degree(), key=lambda item: (-item[1], str(item[0]))
                )[:view_nodes]
                view_edges = graph.subgraph({node for node, _degree in top_nodes}).number_of_edges()
                if "figure_view_edges" in citation and view_edges != citation.get("figure_view_edges"):
                    errors.append("citation figure-view edges disagree with graph")
            except (OSError, ValueError, nx.NetworkXError) as exc:
                errors.append(f"citation graph could not be read: {exc}")

    if (data_dir / "assertion_summary.json").exists():
        summary = _load(data_dir / "assertion_summary.json")
        type_total = sum(summary.get("type_counts", {}).values())
        hypothesis_total = sum(
            sum(bucket.values()) for bucket in summary.get("per_hypothesis", {}).values()
        )
        if type_total != summary.get("total_assertions") or hypothesis_total != type_total:
            errors.append("assertion summary totals are inconsistent")

    nanopub_path = data_dir / "nanopublications.jsonl"
    rdf_report = validate_rdf_package(output_dir)
    errors.extend(f"RDF package: {error}" for error in rdf_report["errors"])
    provenance_path = output_dir / "reports" / "extraction_provenance_summary.json"
    if nanopub_path.exists() and provenance_path.exists():
        nanopubs = deserialize_nanopubs(nanopub_path)
        records = []
        for line in nanopub_path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                records.append(json.loads(line))
        expected = summarize_provenance(records)
        actual = _load(provenance_path)
        if actual != expected:
            errors.append("provenance summary does not match nanopublication JSONL")
        if not expected.get("consistent_provenance", False):
            errors.append("nanopublication provenance is not uniform")
        expected_provenance = {
            field: coverage.get(field)
            for field in ("model_id", "prompt_version", "pipeline_version", "run_id")
        }
        if expected.get("unique_run_ids") != 1:
            errors.append("nanopublication provenance must contain exactly one run_id")
        for record in records:
            assertion = record.get("assertion", {})
            prov = record.get("provenance") or {}
            for field, expected_value in expected_provenance.items():
                if prov.get(field) != expected_value:
                    errors.append(f"nanopublication provenance disagrees with coverage: {field}")
            if prov.get("paper_id") != assertion.get("paper_id"):
                errors.append("nanopublication provenance paper_id disagrees with assertion")
            processing_date = prov.get("processing_date")
            if not processing_date:
                errors.append("nanopublication provenance is missing processing_date")
            else:
                try:
                    datetime.fromisoformat(str(processing_date))
                except ValueError:
                    errors.append("nanopublication provenance has invalid processing_date")
        if coverage.get("failed_papers", 0) or coverage.get("unprocessed_papers", 0):
            errors.append("extraction coverage contains failures or unprocessed papers")
        if coverage.get("assertions") != len(nanopubs):
            errors.append("extraction coverage assertion count does not match nanopublications")
        state_path = data_dir / "extraction_state.json"
        if state_path.exists():
            state = _load(state_path)
            if state.get("status") != "complete":
                errors.append(f"extraction state is not complete: {state.get('status')}")
            if coverage:
                for field in ("run_id", "model_id", "prompt_version", "pipeline_version"):
                    if state.get(field) != coverage.get(field):
                        errors.append(f"extraction state disagrees with coverage: {field}")
        assertion_summary_path = data_dir / "assertion_summary.json"
        if assertion_summary_path.exists():
            assertion_summary = _load(assertion_summary_path)
            if len(nanopubs) != assertion_summary.get("total_assertions", -1):
                errors.append("nanopublication count does not equal assertion total")
            actual_types = Counter(obj.assertion.assertion_type for obj in nanopubs)
            actual_by_hypothesis: dict[str, Counter[str]] = defaultdict(Counter)
            for obj in nanopubs:
                actual_by_hypothesis[obj.assertion.hypothesis_id][
                    obj.assertion.assertion_type
                ] += 1
            expected_types = {
                key: int(value)
                for key, value in assertion_summary.get("type_counts", {}).items()
                if value
            }
            if dict(actual_types) != expected_types:
                errors.append("assertion summary type counts do not match nanopublications")
            expected_by_hypothesis = {
                hypothesis: {
                    key: int(value) for key, value in counts.items() if value
                }
                for hypothesis, counts in assertion_summary.get("per_hypothesis", {}).items()
            }
            actual_by_hypothesis_dict = {
                hypothesis: dict(counts)
                for hypothesis, counts in actual_by_hypothesis.items()
            }
            if actual_by_hypothesis_dict != expected_by_hypothesis:
                errors.append("assertion summary hypothesis counts do not match nanopublications")

            score_path = data_dir / "hypothesis_scores.json"
            if score_path.exists():
                recorded_scores = _load(score_path)
                assertions = [obj.assertion for obj in nanopubs]
                for hypothesis, recorded in recorded_scores.items():
                    expected_score = score_hypothesis(assertions, hypothesis)
                    if abs(float(recorded) - expected_score) > 1e-9:
                        errors.append(f"hypothesis score disagrees with nanopublications: {hypothesis}")

            trends_path = data_dir / "hypothesis_trends.json"
            if trends_path.exists():
                trends = _load(trends_path)
                for hypothesis, series in trends.items():
                    for year_text, point in series.items():
                        year = int(year_text)
                        cumulative = [
                            obj.assertion
                            for obj in nanopubs
                            if (py := paper_years.get(obj.assertion.paper_id)) is not None
                            and py <= year
                        ]
                        relevant = [
                            assertion
                            for assertion in cumulative
                            if assertion.hypothesis_id == hypothesis
                        ]
                        if int(point.get("assertion_count", -1)) != len(relevant):
                            errors.append(
                                f"hypothesis trend assertion count disagrees: {hypothesis}/{year}"
                            )
                        expected_score = score_hypothesis(cumulative, hypothesis)
                        if abs(float(point.get("score", 0.0)) - expected_score) > 1e-9:
                            errors.append(f"hypothesis trend score disagrees: {hypothesis}/{year}")

    if (data_dir / "topics.json").exists():
        topics = _load(data_dir / "topics.json")
        analysis_config = load_analysis_config(project_root / "manuscript" / "config.yaml")
        expected_topics = analysis_config["n_topics"]
        if len(topics) != expected_topics:
            errors.append("topic artifact count does not match configured n_topics")
        stability = _load(data_dir / "topic_stability.json") if (data_dir / "topic_stability.json").exists() else {}
        if stability.get("n_topics") != len(topics):
            errors.append("topic stability artifact does not match topic artifact")
        if "seeds" in stability and list(stability["seeds"]) != list(
            analysis_config["topic_stability_seeds"]
        ):
            errors.append("topic stability seeds do not match configuration")
        if "primary_seed" in stability and stability.get("primary_seed") != analysis_config["seed"]:
            errors.append("topic stability primary seed does not match configuration")
        if "pairwise_comparisons" in stability:
            expected_pairs = len(stability.get("seeds", [])) * (len(stability.get("seeds", [])) - 1) // 2
            if len(stability["pairwise_comparisons"]) != expected_pairs:
                errors.append("topic stability pairwise comparison count is incomplete")

    figure_dir = output_dir / "figures"
    figure_files = sorted(path.name for path in figure_dir.glob("*.png")) if figure_dir.exists() else []
    if len(figure_files) != 16:
        errors.append(f"expected 16 PNG figures, found {len(figure_files)}")
    registry_path = figure_dir / "figure_registry.json"
    if registry_path.exists():
        registry = _load(registry_path)
        registered_files_raw = [item.get("filename") for item in registry.values()]
        registered_files = sorted(
            filename for filename in registered_files_raw if isinstance(filename, str)
        )
        if len(registered_files) != len(registered_files_raw):
            errors.append("figure registry contains an invalid filename")
        if sorted(registered_files) != figure_files:
            errors.append("figure registry does not match generated PNG files")
        if len(registry) != 16:
            errors.append(f"figure registry must contain 16 entries, found {len(registry)}")
        manuscript_paths = list((output_dir / "manuscript").glob("*.md"))
        manuscript_paths.extend((project_root / "manuscript").glob("*.md"))
        rendered_text = "\n".join(path.read_text(encoding="utf-8") for path in manuscript_paths)
        referenced_labels = set(re.findall(r"fig:[A-Za-z0-9_]+", rendered_text))
        registered_labels = {
            str(item.get("label", key)) for key, item in registry.items()
        }
        if referenced_labels != registered_labels:
            missing_labels = sorted(registered_labels - referenced_labels)
            extra_labels = sorted(referenced_labels - registered_labels)
            if missing_labels:
                errors.append("manuscript does not reference registered figures: " + ", ".join(missing_labels))
            if extra_labels:
                errors.append("manuscript references unregistered figures: " + ", ".join(extra_labels))
    else:
        errors.append("missing figure registry")

    variables_path = data_dir / "manuscript_variables.json"
    if variables_path.exists():
        variable_payload = _load(variables_path)
        variables = variable_payload.get("variables", {})
        missing = sorted(set(variable_payload.get("source_tokens", {})) - set(variables))
        if missing:
            errors.append("manuscript variables missing: " + ", ".join(missing))
        rendered_dir = output_dir / "manuscript"
        for path in rendered_dir.glob("*.md"):
            unresolved = TOKEN_RE.findall(path.read_text(encoding="utf-8"))
            if unresolved:
                errors.append(f"unresolved tokens in {path.name}: {sorted(set(unresolved))}")
        for rendered_root in (output_dir / "web", output_dir / "pdf"):
            if rendered_root.exists():
                for path in rendered_root.rglob("*.html"):
                    unresolved = TOKEN_RE.findall(path.read_text(encoding="utf-8"))
                    if unresolved:
                        errors.append(
                            f"unresolved tokens in {path.relative_to(output_dir)}: "
                            f"{sorted(set(unresolved))}"
                        )
                for path in rendered_root.rglob("*.tex"):
                    unresolved = TOKEN_RE.findall(path.read_text(encoding="utf-8"))
                    if unresolved:
                        errors.append(
                            f"unresolved tokens in {path.relative_to(output_dir)}: "
                            f"{sorted(set(unresolved))}"
                        )
        if variable_payload.get("source_files") is not None:
            expected_source_files = {
                str(path.relative_to(project_root)): _file_metadata(path)["sha256"]
                for path in sorted((project_root / "manuscript").glob("*.md"))
                if path.name not in {"AGENTS.md", "README.md", "SKILL.md", "SYNTAX.md"}
            }
            if variable_payload.get("source_files") != expected_source_files:
                errors.append("manuscript variable source-file hashes do not match source files")
        if variable_payload.get("artifact_files") is not None:
            expected_artifacts: dict[str, dict[str, int | str]] = {}
            for base in (data_dir, figure_dir):
                if not base.exists():
                    continue
                for path in sorted(base.rglob("*")):
                    if path.is_file() and path != variables_path:
                        expected_artifacts[str(path.relative_to(project_root))] = _file_metadata(path)
            if variable_payload.get("artifact_files") != expected_artifacts:
                errors.append("manuscript variable artifact hashes do not match current artifacts")
        if variable_payload.get("source_tokens") is not None:
            expected_tokens = collect_manuscript_tokens(project_root / "manuscript")
            if variable_payload.get("source_tokens") != expected_tokens:
                errors.append("manuscript variable source-token inventory is stale")
        if variable_payload.get("source_files") is not None and variable_payload.get("artifact_files") is not None:
            expected_variables = compute_variables(output_dir, project_root=project_root)
            if variables != expected_variables:
                errors.append("manuscript variables do not match current artifacts")

    report = {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": warnings,
        "corpus_size": len(corpus_rows),
        "figure_count": len(figure_files),
    }
    report_path = output_dir / "reports" / "artifact_contract.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


__all__ = ["validate_artifacts"]
