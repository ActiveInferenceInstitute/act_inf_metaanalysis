"""Knowledge graph and nanopublication ontology."""

from __future__ import annotations

from .schema import AIF_NAMESPACE
from .nanopublication import Assertion, Nanopublication
from .hypothesis import Hypothesis, HYPOTHESES, score_hypothesis
from .graph_builder import KnowledgeGraph
from .llm_extraction import extract_assertions_llm, LLMConfig
from .extraction import extract_assertions

__all__ = [
    "AIF_NAMESPACE",
    "Assertion",
    "Nanopublication",
    "Hypothesis",
    "HYPOTHESES",
    "score_hypothesis",
    "KnowledgeGraph",
    "extract_assertions_llm",
    "LLMConfig",
    "extract_assertions",
]
