"""Deterministic rule-based reference-annotator protocols.

These are NOT human annotators. Each protocol is a transparent, reproducible
keyword-and-negation heuristic over the abstract text. They provide an
independent rule-based reference against which the LLM extraction pipeline can
be compared (a reproducibility floor), and a second rule variant for
inter-protocol agreement. Human gold-standard annotation is future work.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

HYPOTHESIS_KEYWORDS: dict[str, list[str]] = {
    "FEP_UNIVERSALITY": ["free energy principle", "universal", "self-organizing"],
    "AIF_OPTIMALITY": ["active inference", "optimal", "decision-making"],
    "MARKOV_BLANKET_REALISM": ["markov blanket", "boundary", "real"],
    "PREDICTIVE_CODING": ["predictive coding", "prediction error", "hierarchical"],
    "SCALABILITY": ["scale", "high-dimensional", "complex environment"],
    "CLINICAL_UTILITY": ["clinical", "psychiatr", "disorder", "symptom"],
    "MORPHOGENESIS": ["morphogen", "development", "embryo"],
    "LANGUAGE_AIF": ["language", "linguistic", "syntax", "semantics"],
}

NEGATION_PATTERNS = [
    r"\bnot\b",
    r"\bno\b",
    r"\bfail",
    r"\blimit",
    r"\bchallenge",
    r"\bcontradict",
    r"\bunlikely\b",
]

EMPIRICAL_PATTERNS = [
    r"\bfmri\b",
    r"\beeg\b",
    r"\bexperiment",
    r"\bempirical",
    r"\bdata\b",
    r"\bmeasure",
    r"\btrial\b",
    r"\bsubject",
]


@dataclass
class LabelResult:
    triage: str
    evidence_status: str
    evidence_type: str
    source_claim: str


def _contains_any(text: str, patterns: list[str]) -> bool:
    lower = text.lower()
    return any(re.search(p, lower) for p in patterns)


def _hypothesis_relevant(text: str, hypothesis_id: str) -> bool:
    keywords = HYPOTHESIS_KEYWORDS.get(hypothesis_id, [])
    lower = text.lower()
    return any(kw in lower for kw in keywords)


def apply_primary_rule_protocol(
    abstract: str,
    hypothesis_id: str,
) -> LabelResult:
    """Primary deterministic rule-based reference annotator (keyword + negation)."""
    text = abstract or ""
    lower = text.lower()
    if not _hypothesis_relevant(text, hypothesis_id):
        return LabelResult("irrelevant", "no_evidence", "none", "")

    negated = _contains_any(lower, NEGATION_PATTERNS)
    empirical = _contains_any(lower, EMPIRICAL_PATTERNS)
    evidence_type = "empirical" if empirical else "theoretical"

    endorsement_patterns = ["we show", "we demonstrate", "our results", "we find", "supports"]
    explicit = any(p in lower for p in endorsement_patterns)

    if negated and not explicit:
        triage = "contradicts"
        status = "mentions"
    elif explicit:
        triage = "supports"
        status = "explicit_claim"
    else:
        triage = "neutral"
        status = "mentions"

    claim = text[:160].strip()
    return LabelResult(triage, status, evidence_type, claim)


def apply_secondary_rule_protocol(
    abstract: str,
    hypothesis_id: str,
) -> LabelResult:
    """Independent second rule variant (for inter-protocol agreement)."""
    text = abstract or ""
    lower = text.lower()
    if not _hypothesis_relevant(text, hypothesis_id):
        return LabelResult("irrelevant", "no_evidence", "none", "")

    empirical = _contains_any(lower, EMPIRICAL_PATTERNS)
    evidence_type = "empirical" if empirical else "theoretical"

    if "however" in lower or "although" in lower:
        triage = "neutral"
        status = "mentions"
    elif any(w in lower for w in ("propose", "introduce", "framework", "model")):
        triage = "supports"
        status = "explicit_claim"
    elif _contains_any(lower, NEGATION_PATTERNS):
        triage = "contradicts"
        status = "mentions"
    else:
        triage = "neutral"
        status = "mentions"

    claim = text[:120].strip()
    return LabelResult(triage, status, evidence_type, claim)
