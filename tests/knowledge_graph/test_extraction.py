from __future__ import annotations

import pytest

from literature.models import Paper
from knowledge_graph.nanopublication import Assertion
from knowledge_graph.extraction import extract_assertions
from knowledge_graph.llm_extraction import LLMConfig

def test_extract_assertions_returns_list() -> None:
    """Basic test to verify extraction wrapper works when LLM mock is provided or bypassed."""
    config = LLMConfig(base_url="http://localhost:11434", model="gemma3:4b")
    # without a running mock server, we just test it accepts the arguments properly
    papers = []
    result = extract_assertions(papers=papers, llm_config=config)
    assert isinstance(result, list)
    assert len(result) == 0
