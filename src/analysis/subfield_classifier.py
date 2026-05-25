"""Keyword-based classification into Active Inference domains.

Maps papers to one of 8 domains organised in three tiers:
  A – Core Theory (A1 formal theory, A2 qualitative philosophy)
  B – Tools & Translation Methods
  C – Domains of Application (C1–C5)

Keyword definitions live in :mod:`analysis.subfield_defaults` and can be
overridden via :func:`configure_subfields` / ``config.yaml`` ``subfield_keywords``.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

from literature.models import Paper

from analysis.subfield_defaults import DEFAULT_SUBFIELDS
from analysis.subfield_registry import (
    SUBFIELDS,
    configure_subfields,
    get_pattern_cache,
    load_subfields_from_config,
)

logger = logging.getLogger(__name__)

__all__ = [
    "DEFAULT_SUBFIELDS",
    "SUBFIELDS",
    "classify_corpus",
    "classify_paper",
    "configure_subfields",
    "load_subfields_from_config",
]


def _get_default_field() -> str:
    """Return the default field name for unclassified papers."""
    for name, info in SUBFIELDS.items():
        kws = [k.lower() for k in info.get("keywords", [])]
        if "free energy principle" in kws or "active inference" in kws:
            return name
    return next(iter(SUBFIELDS))


def classify_paper(paper: Paper) -> str:
    """Classify a paper into a domain by priority-aware keyword matching."""
    text = (paper.title + " " + paper.abstract).lower()
    default_field = _get_default_field()
    pattern_cache = get_pattern_cache()

    scores: list[tuple[int, int, str]] = []
    for field_name, field_info in SUBFIELDS.items():
        patterns = pattern_cache.get(field_name, [])
        count = sum(1 for pattern in patterns if pattern.search(text))
        if count > 0:
            priority = field_info.get("priority", 4)
            scores.append((priority, -count, field_name))

    if not scores:
        logger.debug(
            "Classified '%s' → %s (no keyword matches)", paper.title[:60], default_field
        )
        return default_field

    scores.sort()
    best_field = scores[0][2]
    best_count = -scores[0][1]
    logger.debug(
        "Classified '%s' → %s (%d keyword matches)",
        paper.title[:60],
        best_field,
        best_count,
    )
    return best_field


def classify_corpus(
    papers: list[Paper],
    config_path: Optional[Path] = None,
) -> dict[str, list[Paper]]:
    """Classify all papers in a corpus into domains."""
    if config_path is not None:
        configure_subfields(config_path)

    result: dict[str, list[Paper]] = {name: [] for name in SUBFIELDS}
    for paper in papers:
        result[classify_paper(paper)].append(paper)
    return result
