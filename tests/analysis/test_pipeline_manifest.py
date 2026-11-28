"""Tests for reproducibility manifest generation."""

import json
from pathlib import Path

from analysis.pipeline_manifest import write_pipeline_manifest


def test_write_pipeline_manifest_hashes_outputs(tmp_path: Path) -> None:
    data = tmp_path / "output" / "data"
    data.mkdir(parents=True)
    (data / "artifact.json").write_text("{}", encoding="utf-8")
    (tmp_path / "docs" / "manuscript").mkdir(parents=True)
    (tmp_path / "docs" / "manuscript" / "config.yaml").write_text("analysis: {}\n", encoding="utf-8")
    (tmp_path / "docs" / "manuscript" / "references.bib").write_text("% refs\n", encoding="utf-8")
    (tmp_path / "docs" / "manuscript" / "00_abstract.md").write_text("text\n", encoding="utf-8")
    (tmp_path / "docs" / "reference").mkdir(parents=True)
    (tmp_path / "docs" / "reference" / "tooling_inventory.yaml").write_text("retained_tools: []\n", encoding="utf-8")
    path = write_pipeline_manifest(tmp_path, render_status="pass", validation_status="pass")
    assert path.exists()
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert "output/data/artifact.json" in payload["output_hashes"]
    assert payload["pipeline_version"] == "2.0.6"
    assert payload["prompt_version"] == "v2.0.6"
    assert "run_id" in payload
    assert "as_of_date" in payload
    assert payload["configuration"]["n_topics"] == 8
    assert "docs/manuscript/references.bib" in payload["input_hashes"]
    assert "docs/reference/tooling_inventory.yaml" in payload["input_hashes"]
    assert "docs/manuscript/00_abstract.md" in payload["input_hashes"]
