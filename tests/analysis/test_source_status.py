"""Source admission and manuscript status must describe the same queries."""

import json
from pathlib import Path

import pytest

from analysis.artifact_contract import validate_artifacts
from analysis.pipeline_manifest import write_pipeline_manifest
from manuscript.variables import compute_variables


@pytest.mark.parametrize("failed_first", [True, False])
def test_all_arxiv_queries_govern_every_consumer(tmp_path: Path, failed_first: bool) -> None:
    output = tmp_path / "output"
    reports = output / "reports"
    reports.mkdir(parents=True)
    events = [("arXiv[1]", {"success": False, "error_type": "TimeoutError"}),
              ("arXiv[2]", {"success": True})]
    if not failed_first:
        events.reverse()
    latest = dict(events)
    latest.update({"Semantic Scholar": {"success": True}, "OpenAlex": {"success": True}})
    (reports / "search_provenance.json").write_text(json.dumps({
        "requested_sources": ["arxiv", "semantic_scholar", "openalex"],
        "latest_source_status": latest,
    }))
    contract = validate_artifacts(output, tmp_path)
    assert "literature source did not complete successfully: arxiv" in contract["errors"]
    manifest = json.loads(write_pipeline_manifest(tmp_path).read_text())
    assert manifest["gate_results"]["literature_sources"] == {
        "arxiv": False, "semantic_scholar": True, "openalex": True,
    }
    variables = compute_variables(output, project_root=tmp_path)
    assert variables["SOURCE_COMPLETION_GATE"] == "blocked"
    assert variables["SOURCE_COMPLETION_FAILURES"] == "arxiv"
    assert "arXiv incomplete (TimeoutError)" in variables["SOURCE_COMPLETION_STATUS"]
    assert variables["SOURCE_COMPLETION_SUMMARY"] == "Semantic Scholar, OpenAlex completed; arXiv incomplete"
