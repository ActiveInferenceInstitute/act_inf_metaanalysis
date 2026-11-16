"""Real loopback requests and durable receipts cover zero-result completion."""

from __future__ import annotations

import argparse
import json
from dataclasses import replace
from pathlib import Path

import pytest
from pytest_httpserver import HTTPServer

from knowledge_graph.kg_runner import run_knowledge_graph_pipeline
from knowledge_graph.llm_extraction import LLMConfig, extract_assertions_llm
from literature.corpus import Corpus
from tests.knowledge_graph.llm_extraction_fixtures import (
    httpserver_base_url,
    make_paper,
    valid_llm_response,
)


def _config(server: HTTPServer, path: Path) -> LLMConfig:
    return LLMConfig(
        base_url=httpserver_base_url(server), model="test-model", max_retries=1,
        nanopub_path=str(path), checkpoint_interval=50,
    )


def _success(server: HTTPServer, assessments: list[dict]) -> None:
    server.expect_ordered_request("/api/generate", method="POST").respond_with_json(
        {"response": json.dumps(assessments), "done": True}
    )


@pytest.mark.parametrize("outcome", ["empty", "irrelevant", "below_threshold"])
def test_successful_zero_assertions_are_durable_and_score_only_safe(
    httpserver: HTTPServer, tmp_path: Path, outcome: str,
):
    assessments = valid_llm_response() if outcome != "empty" else []
    for item in assessments:
        if outcome == "irrelevant":
            item["direction"] = "irrelevant"
        else:
            item["confidence"] = 0.1
    _success(httpserver, assessments)
    paper = make_paper()
    nanopubs = tmp_path / "nanopublications.jsonl"
    config = _config(httpserver, nanopubs)
    assert extract_assertions_llm([paper], config, run_id="zero-run") == []
    assert nanopubs.read_bytes() == b""
    state = json.loads((tmp_path / "extraction_state.json").read_text())
    assert state["processed_paper_ids"] == state["zero_assertion_paper_ids"] == [paper.canonical_id]
    for resumed_config in (config, replace(config, max_papers=0)):
        assert extract_assertions_llm([paper], resumed_config) == []
        coverage = json.loads((tmp_path / "extraction_coverage.json").read_text())
        assert coverage["status"] == "complete"
        assert coverage["run_id"] == "zero-run"
        assert coverage["processed_papers"] == 1
        assert coverage["failed_papers"] == coverage["unprocessed_papers"] == 0
    assert len(httpserver.log) == 1


@pytest.mark.parametrize("field", ["model_id", "prompt_version", "pipeline_version", "run_id"])
def test_zero_result_resume_rejects_incompatible_provenance_without_writes(
    httpserver: HTTPServer, tmp_path: Path, field: str,
):
    _success(httpserver, [])
    paper = make_paper()
    config = _config(httpserver, tmp_path / "nanopublications.jsonl")
    extract_assertions_llm([paper], config, run_id="original-run")
    state_path = tmp_path / "extraction_state.json"
    kwargs = {}
    if field == "run_id":
        kwargs["run_id"] = "different-run"
    else:
        state = json.loads(state_path.read_text())
        state[field] = "incompatible"
        state_path.write_text(json.dumps(state))
    before = state_path.read_bytes()
    with pytest.raises(RuntimeError, match="incompatible|does not match"):
        extract_assertions_llm([paper], config, **kwargs)
    assert state_path.read_bytes() == before
    assert len(httpserver.log) == 1


def test_failed_and_unprocessed_are_disjoint_and_resumable(httpserver: HTTPServer, tmp_path: Path):
    _success(httpserver, [])
    httpserver.expect_ordered_request("/api/generate", method="POST").respond_with_data(
        "unavailable", status=503,
    )
    papers = [make_paper(doi=f"10.1/{index}") for index in range(3)]
    config = _config(httpserver, tmp_path / "nanopublications.jsonl")
    assert extract_assertions_llm(papers, replace(config, max_papers=2), run_id="mixed-run") == []
    coverage = json.loads((tmp_path / "extraction_coverage.json").read_text())
    assert coverage["eligible_papers"] == 3
    assert coverage["processed_papers"] == coverage["failed_papers"] == coverage["unprocessed_papers"] == 1
    assert coverage["status"] == "incomplete"
    _success(httpserver, valid_llm_response())
    _success(httpserver, [])
    assertions = extract_assertions_llm(papers, config)
    assert {assertion.paper_id for assertion in assertions} == {papers[1].canonical_id}
    coverage = json.loads((tmp_path / "extraction_coverage.json").read_text())
    assert coverage["status"] == "complete"
    assert coverage["run_id"] == "mixed-run"
    assert coverage["processed_papers"] == 3
    assert coverage["failed_papers"] == coverage["unprocessed_papers"] == 0
    state = json.loads((tmp_path / "extraction_state.json").read_text())
    assert state["zero_assertion_paper_ids"] == [papers[0].canonical_id, papers[2].canonical_id]
    assert len(httpserver.log) == 4


def test_ledger_cannot_replace_missing_positive_assertions(httpserver: HTTPServer, tmp_path: Path):
    _success(httpserver, valid_llm_response())
    paper = make_paper()
    path = tmp_path / "nanopublications.jsonl"
    config = _config(httpserver, path)
    extract_assertions_llm([paper], config)
    path.write_text("")
    with pytest.raises(RuntimeError, match="missing persisted assertions"):
        extract_assertions_llm([paper], config)
    assert len(httpserver.log) == 1


def test_runner_uses_zero_result_ledger_and_clear_removes_its_custody(
    httpserver: HTTPServer, tmp_path: Path,
):
    paper = make_paper()
    corpus = tmp_path / "corpus.jsonl"
    Corpus([paper]).save(corpus)
    output = tmp_path / "output"
    args = argparse.Namespace(
        corpus=str(corpus), output_dir=str(output), config=None,
        llm_model="test-model", llm_url=httpserver_base_url(httpserver),
        checkpoint_interval=50, clear_assertions=False, max_papers=None,
    )
    _success(httpserver, [])
    run_knowledge_graph_pipeline(args, project_root=tmp_path)
    data = output / "data"
    original_run = json.loads((data / "extraction_state.json").read_text())["run_id"]
    args.max_papers = 0
    run_knowledge_graph_pipeline(args, project_root=tmp_path)
    scores = json.loads((data / "hypothesis_scores.json").read_text())
    assert scores and set(scores.values()) == {0.0}
    assert json.loads((data / "hypothesis_trends.json").read_text()) == {}
    assert len(httpserver.log) == 1
    args.clear_assertions = True
    args.max_papers = None
    args.llm_model = "replacement-model"
    _success(httpserver, valid_llm_response())
    run_knowledge_graph_pipeline(args, project_root=tmp_path)
    state = json.loads((data / "extraction_state.json").read_text())
    assert state["status"] == "complete"
    assert state["model_id"] == "replacement-model"
    assert state["run_id"] != original_run
    assert state["zero_assertion_paper_ids"] == []
    assert len(httpserver.log) == 2
