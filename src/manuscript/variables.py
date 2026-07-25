"""Compute template variables from pipeline output data.

Reads pipeline output JSON/JSONL files and computes a dictionary of
template variables that can be injected into manuscript markdown files.
All values are pre-formatted strings ready for LaTeX insertion.

Usage:
    from src.manuscript.variables import compute_variables, inject_variables

    variables = compute_variables(Path("output"))
    rendered = inject_variables(template_content, variables)
"""

from __future__ import annotations

import json
import hashlib
import re
from datetime import datetime, timezone
from pathlib import Path

from config import PIPELINE_VERSION

try:
    from infrastructure.core.logging.utils import get_logger
except ImportError:
    import logging as _logging

    def get_logger(name: str):  # type: ignore[misc]
        """Fallback logger factory used when the infrastructure package is unavailable."""
        return _logging.getLogger(name)


logger = get_logger(__name__)


def _latex_number(n: int) -> str:
    """Format an integer with comma thousand separators.

    Uses plain commas which render correctly in both LaTeX math mode
    and plain text contexts (tables, inline prose).

    Examples:
        775 -> "775"
        1834 -> "1,834"
        28073 -> "28,073"
    """
    s = str(n)
    if len(s) <= 3:
        return s
    # Insert comma separators from right
    parts = []
    while len(s) > 3:
        parts.append(s[-3:])
        s = s[:-3]
    parts.append(s)
    return ",".join(reversed(parts))


def _count_jsonl_lines(path: Path) -> int:
    """Count non-empty lines in a JSONL file."""
    if not path.exists():
        return 0
    count = 0
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                count += 1
    return count


def _load_json(path: Path) -> dict:
    """Load a JSON file, returning error sentinel if missing."""
    if not path.exists():
        logger.warning("Variable source file not found: %s", path)
        return {"_error": f"file_not_found: {path}"}
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def _count_total_references(corpus_path: Path) -> int:
    """Count total references across all papers in a corpus JSONL.

    Sums the length of 'references' or 'referenced_works' lists from each paper.
    """
    if not corpus_path.exists():
        return 0
    total = 0
    with open(corpus_path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            try:
                paper = json.loads(line)
                refs = paper.get("references", paper.get("referenced_works", []))
                if isinstance(refs, list):
                    total += len(refs)
            except json.JSONDecodeError:
                continue
    return total


def _load_inclusion_year_start(project_root: Path | None = None) -> int:
    """Read ``project_config.search.start_year`` from manuscript config."""
    if project_root is None:
        project_root = Path(__file__).resolve().parent.parent.parent
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        return 2000
    try:
        import yaml
    except ImportError:
        return 2000
    with open(config_path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    search_cfg = data.get("project_config", {}).get("search", {})
    return int(search_cfg.get("start_year", 2000))


def _load_project_config(project_root: Path) -> dict:
    """Load the single manuscript configuration source for status variables."""
    config_path = project_root / "manuscript" / "config.yaml"
    if not config_path.exists():
        return {}
    try:
        import yaml
    except ImportError:
        return {}
    data = yaml.safe_load(config_path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


def compute_variables(output_dir: Path, project_root: Path | None = None) -> dict[str, str]:
    """Read all pipeline output JSONs and compute template variables.

    Args:
        output_dir: Path to the project's output/ directory containing
                    corpus.jsonl, temporal_analysis.json, citation_network.json,
                    subfield_classification.json, assertion_summary.json, etc.

    Returns:
        Dictionary mapping variable names (e.g., "CORPUS_SIZE") to
        pre-formatted string values ready for manuscript injection.
        All LaTeX-specific formatting (thousand separators, escaping)
        is applied here.
    """
    variables: dict[str, str] = {}
    data_dir = output_dir / "data"
    if project_root is None:
        project_root = output_dir.parent

    inclusion_start = _load_inclusion_year_start(project_root)
    variables["INCLUSION_YEAR_START"] = str(inclusion_start)

    # ── Corpus size ──────────────────────────────────────────────────
    corpus_path = data_dir / "corpus.jsonl"
    if not corpus_path.exists():
        # Accept a flat output layout for standalone artifact inspection.
        corpus_path = output_dir / "corpus.jsonl"
    corpus_size = _count_jsonl_lines(corpus_path)
    variables["CORPUS_SIZE"] = str(corpus_size)
    variables["CORPUS_SIZE_LATEX"] = _latex_number(corpus_size)
    logger.info("CORPUS_SIZE = %d", corpus_size)

    # ── Temporal analysis ────────────────────────────────────────────
    temporal = _load_json(data_dir / "temporal_analysis.json")
    if temporal.get("_error") is not None:
        temporal = _load_json(output_dir / "temporal_analysis.json")
    if temporal and "_error" not in temporal:
        variables["YEAR_START"] = str(temporal.get("first_year", ""))
        variables["YEAR_END"] = str(temporal.get("last_year", ""))
        variables["CAGR_START_YEAR"] = str(
            temporal.get("cagr_start_year", temporal.get("first_year", ""))
        )
        variables["CAGR_END_YEAR"] = str(
            temporal.get("cagr_end_year", temporal.get("last_year", ""))
        )
        variables["AS_OF_DATE"] = str(temporal.get("as_of_date", ""))
        variables["CURRENT_YEAR"] = str(temporal.get("current_year", ""))
        variables["CURRENT_YEAR_PUBS"] = str(temporal.get("current_year_papers", 0))
        variables["CURRENT_YEAR_STATUS"] = (
            "YTD / partial year"
            if temporal.get("current_year_is_partial", False)
            else "complete year"
        )
        year_end = variables["YEAR_END"]
        if year_end:
            variables["INCLUSION_PERIOD"] = f"{inclusion_start}–{year_end}"
        else:
            variables["INCLUSION_PERIOD"] = str(inclusion_start)
        variables["YEAR_START_PUBS"] = str(
            temporal.get("year_counts", {}).get(
                str(temporal.get("first_year", "")), ""
            )
        )
        variables["PEAK_YEAR"] = str(temporal.get("peak_year", ""))
        
        peak_year_val = str(
            temporal.get("year_counts", {}).get(
                str(temporal.get("peak_year", "")), ""
            )
        )
        variables["PEAK_YEAR_COUNT"] = peak_year_val
        variables["PEAK_YEAR_PUBS"] = peak_year_val

        cagr = temporal.get("cagr", 0)
        variables["CAGR_PCT"] = f"{cagr * 100:.2f}"

        mean_growth = temporal.get("mean_growth_rate", 0)
        variables["MEAN_YOY_GROWTH_PCT"] = (
            f"{mean_growth * 100:.1f}"
        )

        doubling = temporal.get("doubling_time", 0)
        variables["DOUBLING_TIME"] = f"{doubling:.1f}" if doubling else ""
        variables["CAGR_PERIOD"] = (
            f"{variables['CAGR_START_YEAR']}–{variables['CAGR_END_YEAR']}"
        )
    else:
        logger.warning("temporal_analysis.json not found; temporal variables empty")
        variables["INCLUSION_PERIOD"] = str(inclusion_start)

    # ── Citation network ─────────────────────────────────────────────
    citation = _load_json(data_dir / "citation_network.json")
    if citation.get("_error") is not None:
        citation = _load_json(output_dir / "citation_network.json")
    if citation and "_error" not in citation:
        edges = citation.get("num_edges", 0)
        nodes = citation.get("num_nodes", corpus_size)
        components = citation.get("connected_components", 0)
        density = citation.get("density", 0)
        avg_in = citation.get("avg_in_degree", 0)

        variables["CITATION_EDGES"] = _latex_number(edges)
        variables["CITATION_EDGES_RAW"] = str(edges)
        variables["CITATION_NODES"] = str(nodes)
        variables["CITATION_COMPONENTS"] = str(components)
        variables["CITATION_VIEW_NODES"] = str(
            citation.get("figure_view_nodes", min(100, nodes))
        )
        variables["CITATION_VIEW_EDGES"] = _latex_number(
            citation.get("figure_view_edges", edges)
        )

        # Density as percentage
        density_pct = density * 100 if density < 1 else density
        variables["CITATION_DENSITY_PCT"] = f"{density_pct:.2f}"

        # Mean in-degree (use pipeline value directly)
        variables["MEAN_IN_DEGREE"] = f"{avg_in:.1f}"

        # Total references and resolution rate
        # These may need to be computed from corpus data
        total_refs = citation.get("total_references", 0)
        if total_refs > 0:
            variables["CITATION_TOTAL_REFS"] = _latex_number(total_refs)
            variables["CITATION_TOTAL_REFS_RAW"] = str(total_refs)
            resolution = (edges / total_refs) * 100
            variables["CITATION_RESOLUTION_PCT"] = f"{resolution:.1f}"
        else:
            # Compute from corpus JSONL if not in citation JSON
            ref_count = _count_total_references(data_dir / "corpus.jsonl")
            if ref_count == 0:
                ref_count = _count_total_references(output_dir / "corpus.jsonl")
            if ref_count > 0:
                variables["CITATION_TOTAL_REFS"] = _latex_number(ref_count)
                variables["CITATION_TOTAL_REFS_RAW"] = str(ref_count)
                resolution = (edges / ref_count) * 100
                variables["CITATION_RESOLUTION_PCT"] = f"{resolution:.1f}"
            else:
                variables["CITATION_TOTAL_REFS"] = "0"
                variables["CITATION_TOTAL_REFS_RAW"] = "0"
                variables["CITATION_RESOLUTION_PCT"] = "0.0"


        # Communities
        communities = citation.get("num_communities", "")
        variables["CITATION_COMMUNITIES"] = str(communities)
    else:
        logger.warning("citation_network.json not found; citation variables empty")

    # ── Subfield classification ──────────────────────────────────────
    subfield = _load_json(data_dir / "subfield_classification.json")
    if subfield.get("_error") is not None:
        subfield = _load_json(output_dir / "subfield_classification.json")
    if subfield and "_error" not in subfield:
        # Pipeline saves flat dict: {"A1_formal": 75, "A2_philosophy": 73, ...}
        counts = subfield
        total = sum(counts.values()) if isinstance(counts, dict) else corpus_size
        if counts:
            ranked_subfields = sorted(counts.items(), key=lambda item: (-item[1], item[0]))
            variables["TOP_SUBFIELD"] = ranked_subfields[0][0]
            variables["TOP_SUBFIELD_COUNT"] = str(ranked_subfields[0][1])
            subfield_labels = {
                "A1_formal": "A1 formal theory",
                "A2_philosophy": "A2 philosophy",
                "B_tools": "B tools",
                "C1_neuroscience": "C1 neuroscience",
                "C2_robotics": "C2 robotics",
                "C3_language": "C3 language",
                "C4_psychiatry": "C4 psychiatry",
                "C5_biology": "C5 biology",
            }
            variables["TOP_SUBFIELD_LABEL"] = subfield_labels.get(
                ranked_subfields[0][0], ranked_subfields[0][0]
            )
            if len(ranked_subfields) > 1:
                variables["SECOND_SUBFIELD"] = ranked_subfields[1][0]
                variables["SECOND_SUBFIELD_COUNT"] = str(ranked_subfields[1][1])

        domain_keys = {
            "A1_formal": "A1",
            "A2_philosophy": "A2",
            "B_tools": "B",
            "C1_neuroscience": "C1",
            "C2_robotics": "C2",
            "C3_language": "C3",
            "C4_psychiatry": "C4",
            "C5_biology": "C5",
        }

        for key, short in domain_keys.items():
            count = counts.get(key, 0)
            variables[f"{short}_COUNT"] = str(count)
            pct = (count / total * 100) if total > 0 else 0
            variables[f"{short}_PCT"] = f"{pct:.1f}"

        # Domain A total (A1 + A2)
        a_total = counts.get("A1_formal", 0) + counts.get("A2_philosophy", 0)
        variables["A_COUNT"] = str(a_total)
        variables["A_PCT"] = f"{(a_total / total * 100):.1f}" if total > 0 else "0.0"

        # Domain C total
        c_total = sum(
            counts.get(k, 0)
            for k in [
                "C1_neuroscience",
                "C2_robotics",
                "C3_language",
                "C4_psychiatry",
                "C5_biology",
            ]
        )
        variables["C_COUNT"] = str(c_total)
        variables["C_PCT"] = f"{(c_total / total * 100):.1f}" if total > 0 else "0.0"
        domain_totals = {
            "Domain C (Applications)": c_total,
            "Domain B (Tools and Translation)": counts.get("B_tools", 0),
            "Domain A (Core Theory)": a_total,
        }
        ranked_domains = sorted(
            domain_totals.items(), key=lambda item: (-item[1], item[0])
        )
        variables["DOMAIN_RANKING"] = ", ".join(
            f"{label} ({(count / total * 100) if total else 0.0:.1f}\\%)"
            for label, count in ranked_domains
        )
    else:
        logger.warning(
            "subfield_classification.json not found; subfield variables empty"
        )

    # ── Assertion summary (if available) ─────────────────────────────
    assertion = _load_json(data_dir / "assertion_summary.json")
    if assertion.get("_error") is not None:
        assertion = _load_json(output_dir / "assertion_summary.json")
    if assertion and "_error" not in assertion:
        total_assertions = assertion.get("total_assertions", 0)
        variables["TOTAL_ASSERTIONS"] = _latex_number(total_assertions)
        variables["TOTAL_ASSERTIONS_RAW"] = str(total_assertions)

        # Per-hypothesis counts — JSON uses "per_hypothesis" key
        hyp_counts = assertion.get("per_hypothesis", assertion.get("hypothesis_counts", {}))
        for hid, hdata in hyp_counts.items():
            if isinstance(hdata, dict):
                sup = hdata.get("supports", 0)
                con = hdata.get("contradicts", 0)
                neu = hdata.get("neutral", 0)
                total = sup + con + neu
                variables[f"{hid}_SUPPORT"] = str(sup)
                variables[f"{hid}_CONTRADICT"] = str(con)
                variables[f"{hid}_NEUTRAL"] = str(neu)
                variables[f"{hid}_TOTAL"] = str(total)

        # Overall assertion direction percentages
        type_counts = assertion.get("type_counts", {})
        total_sup = type_counts.get("supports", 0)
        total_con = type_counts.get("contradicts", 0)
        total_sc = total_sup + total_con
        if total_sc > 0:
            variables["ASSERTION_SUPPORT_PCT"] = f"{(total_sup/total_sc*100):.1f}"
            variables["ASSERTION_CONTRADICT_PCT"] = f"{(total_con/total_sc*100):.1f}"
        else:
            variables["ASSERTION_SUPPORT_PCT"] = "0.0"
            variables["ASSERTION_CONTRADICT_PCT"] = "0.0"
    else:
        logger.info("assertion_summary.json not found; assertion variables skipped")

    # ── Hypothesis scores (if available) ─────────────────────────────
    scores = _load_json(data_dir / "hypothesis_scores.json")
    if scores.get("_error") is not None:
        scores = _load_json(output_dir / "hypothesis_scores.json")
    if scores and "_error" not in scores:
        for hid, score_val in scores.items():
            if isinstance(score_val, (int, float)):
                variables[f"{hid}_SCORE"] = f"{score_val:+.2f}"
            elif isinstance(score_val, dict):
                s = score_val.get("score", 0)
                variables[f"{hid}_SCORE"] = f"{s:+.2f}"
        numeric_scores = {
            hid: float(value.get("score", 0) if isinstance(value, dict) else value)
            for hid, value in scores.items()
            if isinstance(value, (int, float, dict))
        }
        if numeric_scores:
            top_hypothesis = max(numeric_scores, key=numeric_scores.get)
            variables["TOP_HYPOTHESIS_ID"] = top_hypothesis
            variables["TOP_HYPOTHESIS_SCORE"] = f"{numeric_scores[top_hypothesis]:+.2f}"
            hypothesis_names = {
                "FEP_UNIVERSALITY": "FEP Universality",
                "AIF_OPTIMALITY": "AIF Optimality",
                "MARKOV_BLANKET_REALISM": "Markov Blanket Realism",
                "PREDICTIVE_CODING": "Predictive Coding",
                "SCALABILITY": "Scalability",
                "CLINICAL_UTILITY": "Clinical Utility",
                "MORPHOGENESIS": "Morphogenesis",
                "LANGUAGE_AIF": "Language as Active Inference",
            }
            variables["TOP_HYPOTHESIS_NAME"] = hypothesis_names.get(
                top_hypothesis, top_hypothesis
            )
            variables["POSITIVE_HYPOTHESIS_COUNT"] = str(
                sum(value > 0 for value in numeric_scores.values())
            )
            variables["NEGATIVE_HYPOTHESIS_COUNT"] = str(
                sum(value < 0 for value in numeric_scores.values())
            )
            assertion_counts = assertion.get("per_hypothesis", {}) if assertion else {}
            hypothesis_names = {
                "FEP_UNIVERSALITY": "FEP Universality",
                "AIF_OPTIMALITY": "AIF Optimality",
                "MARKOV_BLANKET_REALISM": "Markov Blanket Realism",
                "PREDICTIVE_CODING": "Predictive Coding",
                "SCALABILITY": "Scalability",
                "CLINICAL_UTILITY": "Clinical Utility",
                "MORPHOGENESIS": "Morphogenesis",
                "LANGUAGE_AIF": "Language as Active Inference",
            }

            def profile(score: float) -> str:
                if score >= 0.9:
                    return "Very strong positive signal"
                if score >= 0.75:
                    return "Strong positive signal"
                if score >= 0.5:
                    return "Positive but diffuse"
                if score > 0:
                    return "Weak positive / contested"
                if score < -0.5:
                    return "Negative signal"
                if score < 0:
                    return "Negative / contested"
                return "Indeterminate"

            rows: list[str] = []
            for hid, score in sorted(
                numeric_scores.items(), key=lambda item: (-item[1], item[0])
            ):
                counts_for_hyp = assertion_counts.get(hid, {})
                supports = int(counts_for_hyp.get("supports", 0))
                neutral = int(counts_for_hyp.get("neutral", 0))
                contradicts = int(counts_for_hyp.get("contradicts", 0))
                total_hyp = supports + neutral + contradicts
                rows.append(
                    f"{hypothesis_names.get(hid, hid)} ({hid.replace('_', r'\_')}) & ${score:+.2f}$ & "
                    f"{supports} & {neutral} & {contradicts} & {total_hyp} & "
                    f"{profile(score)} \\\\"
                )
            variables["HYPOTHESIS_TABLE_ROWS"] = "\n".join(rows)
    else:
        logger.info("hypothesis_scores.json not found; score variables skipped")

    # ── H1–H8 alias mapping ──────────────────────────────────────────
    # Map short HN_ prefixes to full hypothesis ID prefixes for template
    # convenience: {{H1_SCORE}}, {{H1_SUPPORT}}, etc.
    _h_alias = {
        "H1": "FEP_UNIVERSALITY",
        "H2": "AIF_OPTIMALITY",
        "H3": "MARKOV_BLANKET_REALISM",
        "H4": "PREDICTIVE_CODING",
        "H5": "SCALABILITY",
        "H6": "CLINICAL_UTILITY",
        "H7": "MORPHOGENESIS",
        "H8": "LANGUAGE_AIF",
    }
    for short, full in _h_alias.items():
        for suffix in ["_SCORE", "_SUPPORT", "_CONTRADICT", "_NEUTRAL", "_TOTAL"]:
            full_key = f"{full}{suffix}"
            if full_key in variables:
                variables[f"{short}{suffix}"] = variables[full_key]

    # ── Figure count ─────────────────────────────────────────────────
    figures_dir = output_dir / "figures"
    if figures_dir.exists():
        fig_count = len(list(figures_dir.glob("*.png")))
        variables["NUM_FIGURES"] = str(fig_count)
    else:
        variables["NUM_FIGURES"] = "16"
        logger.warning(
            "Figures directory not found at %s; defaulting NUM_FIGURES to 16 (canonical count)",
            figures_dir,
        )

    # ── NMF topics (if available) ────────────────────────────────────
    topics = _load_json(data_dir / "topics.json")
    if isinstance(topics, dict) and topics.get("_error") is not None:
        topics = _load_json(output_dir / "topics.json")
    if topics and "_error" not in topics:
        topic_list = topics if isinstance(topics, list) else topics.get("topics", [])
        variables["NUM_TOPICS"] = str(len(topic_list))
        topic_rows = []
        for topic in topic_list:
            terms = ", ".join(str(term).replace("_", r"\_") for term in topic.get("top_words", []))
            topic_rows.append(
                f"{topic.get('topic_id', len(topic_rows))} & {terms} & Dominant terms: {terms} "
                + r"\\"
            )
        variables["TOPIC_TABLE_ROWS"] = "\n".join(topic_rows)

    topic_stability = _load_json(data_dir / "topic_stability.json")
    if topic_stability and "_error" not in topic_stability:
        variables["TOPIC_STABILITY_MEAN_JACCARD"] = f"{topic_stability.get('mean_jaccard', 0):.3f}"
        variables["TOPIC_STABILITY_MIN_JACCARD"] = f"{topic_stability.get('min_jaccard', 0):.3f}"

    # ── TF-IDF vocabulary size ────────────────────────────────────────
    tfidf = _load_json(data_dir / "tfidf_data.json")
    if tfidf.get("_error") is not None:
        tfidf = _load_json(output_dir / "tfidf_data.json")
    if tfidf and "_error" not in tfidf:
        feature_names = tfidf.get("feature_names", [])
        num_vocab = len(feature_names)
        variables["NUM_VOCAB_FEATURES"] = str(num_vocab)
        variables["NUM_VOCAB_FEATURES_LATEX"] = _latex_number(num_vocab)
        logger.info("NUM_VOCAB_FEATURES = %d", num_vocab)
    else:
        variables["NUM_VOCAB_FEATURES"] = "500"  # Canonical default from pipeline
        variables["NUM_VOCAB_FEATURES_LATEX"] = "500"
        logger.warning("tfidf_data.json not found; defaulting NUM_VOCAB_FEATURES to 500")

    # ── Rule-based reference-annotator agreement metrics ───────────────
    # NOTE: these compare the LLM pipeline against a deterministic keyword-rule
    # reference, NOT human annotators. Variable names/prose say "reference".
    validation = _load_json(data_dir / "validation_metrics.json")
    if validation.get("_error") is not None:
        validation = _load_json(output_dir / "reports" / "validation_metrics.json")
    if validation and "_error" not in validation:
        variables["VAL_N"] = str(validation.get("sample_size", 0))
        kappa = validation.get("kappa_interrule")
        if kappa is not None:
            variables["VAL_KAPPA"] = f"{kappa:.3f}"
        kappa_pipeline = validation.get("kappa_reference_pipeline")
        if kappa_pipeline is not None:
            variables["VAL_KAPPA_PIPELINE"] = f"{kappa_pipeline:.3f}"
        for metric in ("precision", "recall", "f1"):
            val = validation.get(metric)
            if val is not None:
                variables[f"VAL_{metric.upper()}"] = f"{val:.3f}"
        quote_fidelity = validation.get("quote_fidelity_rate")
        if quote_fidelity is not None:
            variables["VAL_QUOTE_FIDELITY"] = f"{quote_fidelity:.3f}"
        else:
            # No verbatim quotes stored in the current abstract-only corpus:
            # report N/A rather than a spurious 0.0 that reads as "0% faithful".
            variables["VAL_QUOTE_FIDELITY"] = "n/a"
        taxonomy = validation.get("error_taxonomy_rates", {})
        for err_key, rate in taxonomy.items():
            safe = err_key.upper().replace(" ", "_")
            variables[f"VAL_ERR_{safe}"] = f"{rate:.3f}"

    # ── Hypothesis scoring sensitivity ───────────────────────────────
    sensitivity = _load_json(data_dir / "hypothesis_sensitivity.json")
    if sensitivity.get("_error") is not None:
        sensitivity = _load_json(output_dir / "data" / "hypothesis_sensitivity.json")
    if sensitivity and "_error" not in sensitivity:
        spearman = sensitivity.get("rank_stability_spearman")
        if spearman is not None:
            variables["SENSITIVITY_SPEARMAN"] = f"{spearman:.3f}"
        rank_changes = sensitivity.get("rank_change_count")
        if rank_changes is not None:
            variables["SENSITIVITY_RANK_FLIPS"] = str(rank_changes)
        default_scores = sensitivity.get("default_scores", {})
        policy_scores = sensitivity.get("policy_comparisons", {})
        sign_changes: set[str] = set()
        for comparison in policy_scores.values():
            for hid, score in comparison.get("scores", {}).items():
                default = float(default_scores.get(hid, 0.0))
                observed = float(score)
                if (default > 0 > observed) or (default < 0 < observed):
                    sign_changes.add(hid)
        variables["SENSITIVITY_SIGN_CHANGE_COUNT"] = str(len(sign_changes))

    # ── Extraction provenance (model / prompt version) ───────────────
    provenance = _load_json(output_dir / "reports" / "extraction_provenance_summary.json")
    if provenance and "_error" not in provenance:
        models = provenance.get("unique_models", {})
        if isinstance(models, dict) and models:
            variables["PROV_MODEL"] = max(models, key=models.get)
        prompts = provenance.get("prompt_versions", {})
        if isinstance(prompts, dict) and prompts:
            variables["PROV_PROMPT_VERSION"] = max(prompts, key=prompts.get)
        pipelines = provenance.get("pipeline_versions", {})
        if isinstance(pipelines, dict) and pipelines:
            variables["PROV_PIPELINE_VERSION"] = max(pipelines, key=pipelines.get)

    coverage = _load_json(data_dir / "extraction_coverage.json")
    if coverage and "_error" not in coverage:
        variables["EXTRACTION_ELIGIBLE"] = str(coverage.get("eligible_papers", 0))
        variables["EXTRACTION_PROCESSED"] = str(coverage.get("processed_papers", 0))
        variables["EXTRACTION_FAILED"] = str(coverage.get("failed_papers", 0))
        eligible = coverage.get("eligible_papers", 0)
        variables["EXTRACTION_COVERAGE_PCT"] = (
            f"{coverage.get('processed_papers', 0) / eligible * 100:.1f}"
            if eligible
            else "0.0"
        )

    # ── Publication/status front matter ─────────────────────────────
    project_config = _load_project_config(project_root)
    pipeline_config = project_config.get("project_config", {}).get("pipeline", {})
    llm_config = project_config.get("project_config", {}).get("llm_extraction", {})
    variables["PIPELINE_VERSION"] = str(
        pipeline_config.get("pipeline_version", variables.get("PROV_PIPELINE_VERSION", PIPELINE_VERSION))
    )
    variables["PROMPT_VERSION"] = str(
        pipeline_config.get("prompt_version", variables.get("PROV_PROMPT_VERSION", ""))
    )
    variables["MODEL_ID"] = str(
        variables.get("PROV_MODEL", llm_config.get("model", ""))
    )
    variables["CURRENT_YEAR_POLICY"] = str(
        project_config.get("analysis", {}).get(
            "complete_year_policy", "exclude_current_partial_year_from_cagr"
        )
    )

    search_report = _load_json(output_dir / "reports" / "search_provenance.json")
    latest_sources = search_report.get("latest_source_status", {}) if "_error" not in search_report else {}
    source_labels = {
        "arxiv": "arXiv",
        "semantic_scholar": "Semantic Scholar",
        "openalex": "OpenAlex",
    }
    source_states: list[str] = []
    failed_sources: list[str] = []
    for key, label in source_labels.items():
        if key == "arxiv":
            events = [event for name, event in latest_sources.items() if str(name).lower().startswith("arxiv[")]
            event = events[-1] if events else {}
        else:
            event = latest_sources.get(label, {})
        if event.get("success"):
            source_states.append(f"{label} complete")
        else:
            detail = event.get("error_type") or event.get("error") or "not completed"
            source_states.append(f"{label} incomplete ({detail})")
            failed_sources.append(key)
    variables["SOURCE_COMPLETION_STATUS"] = "; ".join(source_states) or "source status unavailable"
    variables["SOURCE_COMPLETION_GATE"] = "pass" if not failed_sources else "blocked"
    variables["SOURCE_COMPLETION_FAILURES"] = ", ".join(failed_sources) or "none"

    pdf_path = output_dir / "pdf" / "act_inf_metaanalysis_combined.pdf"
    html_path = output_dir / "web" / "index.html"
    render_pass = pdf_path.exists() and pdf_path.stat().st_size > 0 and html_path.exists() and html_path.stat().st_size > 0
    variables["RENDER_STATUS"] = "PDF and HTML pass" if render_pass else "render pending or incomplete"
    rdf_report = _load_json(output_dir / "reports" / "rdf_package_validation.json")
    variables["RDF_PACKAGE_STATUS"] = str(rdf_report.get("status", "not run"))
    preflight = _load_json(output_dir / "reports" / "release_preflight.json")
    variables["RELEASE_PREFLIGHT_STATUS"] = str(preflight.get("status", "not run"))
    tooling = _load_json(output_dir / "reports" / "tooling_verification.json")
    if tooling and "_error" not in tooling:
        verified = tooling.get("verified_count", 0)
        total = tooling.get("registry_count", 0)
        variables["TOOLING_VERIFICATION_STATUS"] = (
            "pass"
            if tooling.get("status") == "pass"
            else f"partial ({verified}/{total} verified)"
        )
    else:
        variables["TOOLING_VERIFICATION_STATUS"] = "not run"
    variables["SNAPSHOT_STATUS"] = (
        f"{variables.get('AS_OF_DATE', 'undated')} snapshot; source gate {variables['SOURCE_COMPLETION_GATE']}; "
        f"{variables.get('EXTRACTION_PROCESSED', '0')}/{variables.get('EXTRACTION_ELIGIBLE', '0')} eligible papers processed; "
        f"{variables.get('TOTAL_ASSERTIONS', '0')} assertions; {variables['RENDER_STATUS']}"
    )

    logger.info(
        "Computed %d template variables from pipeline output", len(variables)
    )
    return variables


def inject_variables(
    content: str,
    variables: dict[str, str],
    filename: str = "<unknown>",
    lenient: bool = False,
) -> str:
    """Replace {{VAR_NAME}} placeholders in content with variable values.

    Args:
        content: Manuscript markdown content with {{VAR}} placeholders.
        variables: Dictionary of variable name -> formatted value.
        filename: Source filename for logging.
        lenient: If True, warn and leave unresolved placeholders as-is.
                If False (default), raise RuntimeError on any unresolved variable.

    Returns:
        Content with all recognized placeholders replaced.

    Raises:
        RuntimeError: If lenient=False and unresolved variables remain.
    """
    replaced_count = 0
    missing_vars = []

    def replacer(match: re.Match) -> str:
        """Replace a matched placeholder with its corresponding variable value."""
        nonlocal replaced_count
        var_name = match.group(1)
        if var_name in variables:
            replaced_count += 1
            return variables[var_name]
        else:
            missing_vars.append(var_name)
            return match.group(0)  # Leave unresolved

    result = re.sub(r"\{\{(\w+)\}\}", replacer, content)

    if replaced_count > 0:
        logger.info(
            "Injected %d variables into %s", replaced_count, filename
        )

    if missing_vars:
        unique_missing = sorted(set(missing_vars))
        if lenient:
            logger.warning(
                "Unresolved variables in %s: %s",
                filename,
                ", ".join(unique_missing),
            )
        else:
            raise RuntimeError(
                f"Unresolved variables in {filename}: {', '.join(unique_missing)}"
            )

    return result


def write_zenodo_metadata(
    variables: dict[str, str],
    output_path: Path,
    *,
    doi: str = "10.5281/zenodo.19461934",
    version: str = PIPELINE_VERSION,
) -> Path:
    """Write Zenodo deposit metadata from injected template variables."""
    period = variables.get("INCLUSION_PERIOD", "")
    title = (
        f"A Living Meta-Analysis Architecture for Active Inference ({period})"
        if period
        else "A Living Meta-Analysis Architecture for Active Inference"
    )
    description = (
        f"Corpus N={variables.get('CORPUS_SIZE', '?')}; "
        f"inclusion from {variables.get('INCLUSION_YEAR_START', '?')}; "
        f"rule-based reference agreement n={variables.get('VAL_N', '?')}, "
        f"inter-rule κ={variables.get('VAL_KAPPA', '?')}, "
        f"pipeline-vs-reference precision={variables.get('VAL_PRECISION', '?')}, "
        f"recall={variables.get('VAL_RECALL', '?')}. "
        "Reference labels are deterministic keyword rules, not human annotation. "
        "Hypothesis scores report citation-weighted evidence mapping and triage, "
        "not scientific confirmation."
    )
    payload = {
        "title": title,
        "description": description,
        "version": version,
        "doi": doi,
    }
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return output_path


TOKEN_RE = re.compile(r"\{\{([A-Z][A-Z0-9_]*)\}\}")


def collect_manuscript_tokens(manuscript_dir: Path) -> dict[str, list[str]]:
    """Return uppercase manuscript tokens and the source files using them."""
    tokens: dict[str, list[str]] = {}
    for path in sorted(Path(manuscript_dir).glob("*.md")):
        if path.name in {"AGENTS.md", "README.md", "SKILL.md", "SYNTAX.md"}:
            continue
        for token in sorted(set(TOKEN_RE.findall(path.read_text(encoding="utf-8")))):
            tokens.setdefault(token, []).append(path.name)
    return tokens


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def write_manuscript_variables(
    output_dir: Path,
    project_root: Path,
    variables: dict[str, str],
) -> Path:
    """Persist variables, token coverage, and source/artifact hashes."""
    manuscript_dir = project_root / "manuscript"
    source_files = {
        str(path.relative_to(project_root)): _sha256(path)
        for path in sorted(manuscript_dir.glob("*.md"))
        if path.name not in {"AGENTS.md", "README.md", "SKILL.md", "SYNTAX.md"}
    }
    artifact_files: dict[str, dict[str, int | str]] = {}
    for base in (output_dir / "data", output_dir / "figures"):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if path.is_file():
                artifact_files[str(path.relative_to(project_root))] = {
                    "sha256": _sha256(path),
                    "size_bytes": path.stat().st_size,
                }
    payload = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "variables": variables,
        "source_tokens": collect_manuscript_tokens(manuscript_dir),
        "variable_keys": sorted(variables),
        "source_files": source_files,
        "artifact_files": artifact_files,
    }
    path = output_dir / "data" / "manuscript_variables.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path
