"""Tests for knowledge_graph.llm_extraction module.

Tests prompt construction, JSON response parsing, assertion building,
error handling, and batch extraction using pytest-httpserver to serve
the Ollama API shape over real HTTP.
"""

from __future__ import annotations

import json
import pytest
from pytest_httpserver import HTTPServer

from knowledge_graph.llm_extraction import (
    LLMConfig,
    _parse_llm_response,
    assess_paper_hypotheses,
    build_prompt,
    extract_assertions_llm,
    _hypothesis_dicts,
)
from knowledge_graph.extraction import extract_assertions
from literature.models import Paper


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

def _make_paper(**overrides) -> Paper:
    """Create a minimal Paper for testing."""
    defaults = dict(
        title="Active Inference and Free Energy",
        abstract="This paper explores the free energy principle as a universal account of self-organization.",
        authors=[],
        year=2023,
        doi="10.1234/test",
        arxiv_id=None,
        s2_id=None,
        openalex_id=None,
        citation_count=42,
        references=[],
    )
    defaults.update(overrides)
    return Paper(**defaults)


def _valid_llm_response() -> list[dict]:
    """Generate a valid LLM response JSON array."""
    return [
        {
            "hypothesis_id": "FEP_UNIVERSALITY",
            "direction": "supports",
            "confidence": 0.85,
            "reasoning": "The paper provides formal proofs extending FEP to non-equilibrium systems.",
        },
        {
            "hypothesis_id": "AIF_OPTIMALITY",
            "direction": "irrelevant",
            "confidence": 0.0,
            "reasoning": "The paper does not address planning or decision-making.",
        },
        {
            "hypothesis_id": "PREDICTIVE_CODING",
            "direction": "contradicts",
            "confidence": 0.6,
            "reasoning": "The paper challenges standard predictive coding assumptions.",
        },
        {
            "hypothesis_id": "MARKOV_BLANKET_REALISM",
            "direction": "neutral",
            "confidence": 0.5,
            "reasoning": "The paper mentions Markov blankets but does not take a stance.",
        },
        {
            "hypothesis_id": "SCALABILITY",
            "direction": "irrelevant",
            "confidence": 0.0,
            "reasoning": "Not relevant.",
        },
        {
            "hypothesis_id": "CLINICAL_UTILITY",
            "direction": "irrelevant",
            "confidence": 0.0,
            "reasoning": "Not relevant.",
        },
        {
            "hypothesis_id": "MORPHOGENESIS",
            "direction": "irrelevant",
            "confidence": 0.0,
            "reasoning": "Not relevant.",
        },
        {
            "hypothesis_id": "LANGUAGE_AIF",
            "direction": "irrelevant",
            "confidence": 0.0,
            "reasoning": "Not relevant.",
        },
    ]


# ---------------------------------------------------------------------------
# Test: prompt construction
# ---------------------------------------------------------------------------

class TestBuildPrompt:
    def test_prompt_contains_paper_info(self):
        paper = _make_paper()
        hypotheses = _hypothesis_dicts()
        prompt = build_prompt(paper, hypotheses)

        assert "Active Inference and Free Energy" in prompt
        assert "free energy principle" in prompt
        assert "FEP_UNIVERSALITY" in prompt
        assert "AIF_OPTIMALITY" in prompt
        assert "JSON array" in prompt

    def test_prompt_with_long_abstract(self):
        paper = _make_paper(abstract="x" * 5000)
        prompt = build_prompt(paper, _hypothesis_dicts())
        assert len(prompt) > 5000

    def test_hypothesis_dicts_returns_all_eight(self):
        dicts = _hypothesis_dicts()
        assert len(dicts) == 8
        ids = {d["id"] for d in dicts}
        assert "FEP_UNIVERSALITY" in ids
        assert "LANGUAGE_AIF" in ids


# ---------------------------------------------------------------------------
# Test: JSON response parsing
# ---------------------------------------------------------------------------

class TestParseResponse:
    def test_clean_json_array(self):
        raw = json.dumps(_valid_llm_response())
        result = _parse_llm_response(raw)
        assert len(result) == 8
        assert result[0]["hypothesis_id"] == "FEP_UNIVERSALITY"

    def test_json_with_markdown_fences(self):
        raw = "```json\n" + json.dumps(_valid_llm_response()) + "\n```"
        result = _parse_llm_response(raw)
        assert len(result) == 8

    def test_json_with_surrounding_text(self):
        raw = "Here is the analysis:\n" + json.dumps(_valid_llm_response()) + "\nEnd."
        result = _parse_llm_response(raw)
        assert len(result) == 8

    def test_no_json_raises_value_error(self):
        with pytest.raises(ValueError, match="No JSON array"):
            _parse_llm_response("This is just commentary with no JSON.")

    def test_invalid_json_raises_value_error(self):
        with pytest.raises(ValueError, match="Failed to parse"):
            _parse_llm_response("[{invalid json}]")

    def test_non_array_raises_value_error(self):
        with pytest.raises(ValueError, match="No JSON array"):
            _parse_llm_response('{"key": "value"}')


# ---------------------------------------------------------------------------
# Test: single-paper assessment (via httpserver)
# ---------------------------------------------------------------------------

class TestAssessPaperHypotheses:
    def test_successful_assessment(self, httpserver: HTTPServer):
        """LLM returns valid JSON → assertions are created correctly."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],  # strip trailing slash
            model="test-model",
            max_retries=1,
        )

        paper = _make_paper()
        assertions = assess_paper_hypotheses(paper, config)

        # "irrelevant" entries are excluded → 3 should remain
        assert len(assertions) == 3

        # Check the supporting assertion
        fep = [a for a in assertions if a.hypothesis_id == "FEP_UNIVERSALITY"]
        assert len(fep) == 1
        assert fep[0].assertion_type == "supports"
        assert fep[0].confidence == 0.85
        assert fep[0].citation_count == 42

        # Check the contradicting assertion
        pc = [a for a in assertions if a.hypothesis_id == "PREDICTIVE_CODING"]
        assert len(pc) == 1
        assert pc[0].assertion_type == "contradicts"
        assert pc[0].confidence == 0.6

        # Check the neutral assertion
        mb = [a for a in assertions if a.hypothesis_id == "MARKOV_BLANKET_REALISM"]
        assert len(mb) == 1
        assert mb[0].assertion_type == "neutral"

    def test_invalid_directions_skipped(self, httpserver: HTTPServer):
        """Unknown directions are silently skipped."""
        response_data = [
            {"hypothesis_id": "FEP_UNIVERSALITY", "direction": "maybe", "confidence": 0.5, "reasoning": "unsure"},
            {"hypothesis_id": "AIF_OPTIMALITY", "direction": "supports", "confidence": 0.7, "reasoning": "ok"},
        ]
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json({"response": json.dumps(response_data), "done": True})

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
        )

        assertions = assess_paper_hypotheses(_make_paper(), config)
        assert len(assertions) == 1
        assert assertions[0].hypothesis_id == "AIF_OPTIMALITY"

    def test_unknown_hypothesis_ids_skipped(self, httpserver: HTTPServer):
        """Hypothesis IDs not in the standard set are skipped."""
        response_data = [
            {"hypothesis_id": "MADE_UP_THING", "direction": "supports", "confidence": 0.9, "reasoning": "nope"},
        ]
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json({"response": json.dumps(response_data), "done": True})

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
        )

        assertions = assess_paper_hypotheses(_make_paper(), config)
        assert len(assertions) == 0

    def test_retries_on_parse_failure(self, httpserver: HTTPServer):
        """First response is garbage JSON, second is valid → succeeds."""
        # First request: bad response
        httpserver.expect_ordered_request(
            "/api/generate", method="POST"
        ).respond_with_json({"response": "Not valid JSON at all", "done": True})

        # Second request: valid response
        httpserver.expect_ordered_request(
            "/api/generate", method="POST"
        ).respond_with_json({
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        })

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=2,
            retry_delay=0.01,  # fast for tests
        )

        assertions = assess_paper_hypotheses(_make_paper(), config)
        assert len(assertions) == 3  # 3 non-irrelevant

    def test_all_retries_exhausted_raises_runtime_error(self, httpserver: HTTPServer):
        """All retries fail → RuntimeError."""
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json({"response": "garbage", "done": True})

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=2,
            retry_delay=0.01,
        )

        with pytest.raises(RuntimeError, match="failed after 2 retries"):
            assess_paper_hypotheses(_make_paper(), config)

    def test_confidence_clamped(self, httpserver: HTTPServer):
        """Confidence values outside [0, 1] are clamped."""
        response_data = [
            {"hypothesis_id": "FEP_UNIVERSALITY", "direction": "supports", "confidence": 1.5, "reasoning": "high"},
            {"hypothesis_id": "AIF_OPTIMALITY", "direction": "contradicts", "confidence": -0.3, "reasoning": "low"},
        ]
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json({"response": json.dumps(response_data), "done": True})

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
        )

        assertions = assess_paper_hypotheses(_make_paper(), config)
        assert assertions[0].confidence == 1.0
        assert assertions[1].confidence == 0.0


# ---------------------------------------------------------------------------
# Test: batch extraction
# ---------------------------------------------------------------------------

class TestExtractAssertionsLLM:
    def test_batch_extraction(self, httpserver: HTTPServer):
        """Multiple papers processed sequentially."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
        )

        papers = [_make_paper(doi=f"10.1234/p{i}") for i in range(3)]
        assertions = extract_assertions_llm(papers, config)

        # 3 papers × 3 non-irrelevant assertions each = 9
        assert len(assertions) == 9

    def test_papers_without_abstract_skipped(self, httpserver: HTTPServer):
        """Papers without abstracts are silently skipped."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
        )

        papers = [
            _make_paper(abstract="", doi="10.1234/empty"),
            _make_paper(doi="10.1234/with_abstract"),
        ]
        assertions = extract_assertions_llm(papers, config)

        # Only 1 paper processed (the one with abstract)
        assert len(assertions) == 3


# ---------------------------------------------------------------------------
# Test: unified entry point (extraction.py)
# ---------------------------------------------------------------------------

class TestExtractAssertions:
    def test_default_config(self, httpserver: HTTPServer):
        """Without explicit config, uses default LLMConfig."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
        )

        papers = [_make_paper()]
        assertions = extract_assertions(papers, llm_config=config)
        assert len(assertions) == 3
        # LLM method produces assertions with "llm_" prefix
        assert all(a.assertion_id.startswith("llm_") for a in assertions)

    def test_custom_config(self, httpserver: HTTPServer):
        """Custom LLMConfig is forwarded correctly."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="custom-model",
            temperature=0.5,
            max_retries=1,
        )

        papers = [_make_paper()]
        assertions = extract_assertions(papers, llm_config=config)
        assert len(assertions) == 3


# ---------------------------------------------------------------------------
# Test: LLMConfig defaults
# ---------------------------------------------------------------------------

class TestLLMConfig:
    def test_defaults(self):
        config = LLMConfig()
        assert config.base_url == "http://localhost:11434"
        assert config.model == "gemma3:4b"
        assert config.temperature == 0.1
        assert config.max_retries == 3
        assert config.nanopub_path is None
        assert config.checkpoint_interval == 50
        assert config.max_papers is None

    def test_custom_values(self):
        config = LLMConfig(model="llama3:8b", temperature=0.5)
        assert config.model == "llama3:8b"
        assert config.temperature == 0.5


# ---------------------------------------------------------------------------
# Test: Nanopub-based resume (replaces old checkpoint tests)
# ---------------------------------------------------------------------------

class TestNanopubResume:
    def test_resume_skips_processed(self, httpserver: HTTPServer, tmp_path):
        """Resume skips papers already in the nanopubs file."""
        from knowledge_graph.nanopublication import (
            Assertion, create_nanopub, serialize_nanopubs,
        )

        nanopub_path = tmp_path / "nanopublications.jsonl"

        # Paper with doi="10.1/a" will have canonical_id="doi:10.1/a"
        paper1_cid = "doi:10.1/a"
        existing_assertion = Assertion(
            assertion_id=f"llm_{paper1_cid}_FEP_UNIVERSALITY",
            paper_id=paper1_cid,
            claim="Pre-existing",
            assertion_type="supports",
            hypothesis_id="FEP_UNIVERSALITY",
            confidence=0.8,
            citation_count=3,
        )
        serialize_nanopubs(
            [create_nanopub(existing_assertion, attribution="test")],
            nanopub_path,
        )

        # Set up server for paper2 only
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            nanopub_path=str(nanopub_path),
            checkpoint_interval=100,
        )

        papers = [
            _make_paper(doi="10.1/a", title="Paper 1"),
            _make_paper(doi="10.1/b", title="Paper 2"),
        ]
        assertions = extract_assertions_llm(papers, config)
        # Should have 1 from existing nanopubs + 3 from paper2
        assert len(assertions) == 4

    def test_fresh_run_no_nanopub_file(self, httpserver: HTTPServer, tmp_path):
        """When no nanopub file exists, processes all papers."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        nanopub_path = tmp_path / "nanopublications.jsonl"
        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            nanopub_path=str(nanopub_path),
            checkpoint_interval=100,
        )

        papers = [_make_paper(doi=f"10.1/{i}") for i in range(2)]
        assertions = extract_assertions_llm(papers, config)
        # 2 papers × 3 non-irrelevant assertions = 6
        assert len(assertions) == 6
        # Nanopub file should have been created
        assert nanopub_path.exists()

    def test_nanopub_file_updated_after_extraction(self, httpserver: HTTPServer, tmp_path):
        """After extraction, nanopub file on disk contains all results."""
        from knowledge_graph.nanopublication import deserialize_nanopubs

        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        nanopub_path = tmp_path / "nanopublications.jsonl"
        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            nanopub_path=str(nanopub_path),
            checkpoint_interval=100,
        )

        papers = [_make_paper(doi="10.1/x")]
        extract_assertions_llm(papers, config)

        nanopubs = deserialize_nanopubs(nanopub_path)
        assert len(nanopubs) == 3  # 3 non-irrelevant
        assert all(
            np_obj.assertion.paper_id == "doi:10.1/x"
            for np_obj in nanopubs
        )

    def test_logs_nanopub_path_on_fresh_run(self, httpserver: HTTPServer, tmp_path, caplog):
        """Fresh run logs the nanopub output path."""
        import logging
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        nanopub_path = tmp_path / "nanopublications.jsonl"
        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            nanopub_path=str(nanopub_path),
            checkpoint_interval=100,
        )

        papers = [_make_paper(doi="10.1/log")]
        with caplog.at_level(logging.INFO, logger="knowledge_graph.llm_extraction"):
            extract_assertions_llm(papers, config)

        # Should log persistence file path and completion path
        assert any("Nanopub persistence file" in m for m in caplog.messages)
        assert any("Nanopublications saved" in m for m in caplog.messages)
        assert any(str(nanopub_path) in m for m in caplog.messages)

    def test_logs_resume_info(self, httpserver: HTTPServer, tmp_path, caplog):
        """Resume run logs how many papers were already processed."""
        import logging
        from knowledge_graph.nanopublication import (
            Assertion, create_nanopub, serialize_nanopubs,
        )

        nanopub_path = tmp_path / "nanopublications.jsonl"
        existing = Assertion(
            assertion_id="llm_doi:10.1/a_FEP_UNIVERSALITY",
            paper_id="doi:10.1/a",
            claim="existing",
            assertion_type="supports",
            hypothesis_id="FEP_UNIVERSALITY",
            confidence=0.8,
            citation_count=3,
        )
        serialize_nanopubs(
            [create_nanopub(existing, attribution="test")],
            nanopub_path,
        )

        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            nanopub_path=str(nanopub_path),
            checkpoint_interval=100,
        )

        papers = [
            _make_paper(doi="10.1/a", title="Paper A"),
            _make_paper(doi="10.1/b", title="Paper B"),
        ]
        with caplog.at_level(logging.INFO, logger="knowledge_graph.llm_extraction"):
            extract_assertions_llm(papers, config)

        assert any("Resuming" in m for m in caplog.messages)
        assert any("1 papers already processed" in m for m in caplog.messages)


# ---------------------------------------------------------------------------
# Test: max_papers cap
# ---------------------------------------------------------------------------

class TestMaxPapers:
    def test_max_papers_limits_extraction(self, httpserver: HTTPServer):
        """Setting max_papers stops extraction after that many papers."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            max_papers=2,
        )

        papers = [_make_paper(doi=f"10.1234/p{i}") for i in range(5)]
        assertions = extract_assertions_llm(papers, config)

        # Only 2 papers processed × 3 assertions each = 6
        assert len(assertions) == 6

    def test_max_papers_none_processes_all(self, httpserver: HTTPServer):
        """max_papers=None (default) processes all papers."""
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            max_papers=None,
        )

        papers = [_make_paper(doi=f"10.1234/p{i}") for i in range(4)]
        assertions = extract_assertions_llm(papers, config)

        # All 4 papers × 3 assertions = 12
        assert len(assertions) == 12

    def test_max_papers_with_resume(self, httpserver: HTTPServer, tmp_path):
        """max_papers counts only newly processed papers, not resumed ones."""
        from knowledge_graph.nanopublication import (
            Assertion, create_nanopub, serialize_nanopubs,
        )

        nanopub_path = tmp_path / "nanopublications.jsonl"
        existing = Assertion(
            assertion_id="llm_doi:10.1/a_FEP_UNIVERSALITY",
            paper_id="doi:10.1/a",
            claim="existing",
            assertion_type="supports",
            hypothesis_id="FEP_UNIVERSALITY",
            confidence=0.8,
            citation_count=3,
        )
        serialize_nanopubs(
            [create_nanopub(existing, attribution="test")],
            nanopub_path,
        )

        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            nanopub_path=str(nanopub_path),
            checkpoint_interval=100,
            max_papers=1,  # only process 1 NEW paper
        )

        papers = [
            _make_paper(doi="10.1/a", title="Already done"),
            _make_paper(doi="10.1/b", title="New 1"),
            _make_paper(doi="10.1/c", title="New 2"),
        ]
        assertions = extract_assertions_llm(papers, config)

        # 1 from resumed + 3 from 1 new paper = 4
        assert len(assertions) == 4

    def test_max_papers_logs_limit(self, httpserver: HTTPServer, caplog):
        """When max_papers is set, a log message announces the limit."""
        import logging
        response_body = {
            "response": json.dumps(_valid_llm_response()),
            "done": True,
        }
        httpserver.expect_request(
            "/api/generate", method="POST"
        ).respond_with_json(response_body)

        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            max_papers=2,
        )

        papers = [_make_paper(doi=f"10.1234/p{i}") for i in range(5)]
        with caplog.at_level(logging.INFO, logger="knowledge_graph.llm_extraction"):
            extract_assertions_llm(papers, config)

        assert any("max_papers=2" in m for m in caplog.messages)
        assert any("stopping extraction early" in m for m in caplog.messages)

    def test_max_papers_zero_processes_none(self, httpserver: HTTPServer):
        """max_papers=0 means no papers are processed."""
        config = LLMConfig(
            base_url=httpserver.url_for("")[:-1],
            model="test-model",
            max_retries=1,
            max_papers=0,
        )

        papers = [_make_paper(doi="10.1234/p0")]
        assertions = extract_assertions_llm(papers, config)
        assert len(assertions) == 0

