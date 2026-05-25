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
import re
from pathlib import Path
from typing import Optional

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


def compute_variables(output_dir: Path) -> dict[str, str]:
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

    # ── Corpus size ──────────────────────────────────────────────────
    corpus_path = data_dir / "corpus.jsonl"
    if not corpus_path.exists():
        # Fall back to output root for legacy layout
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
    else:
        logger.warning("temporal_analysis.json not found; temporal variables empty")

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
