"""Tests for reproducibility manifest generation."""

from pathlib import Path

from analysis.pipeline_manifest import write_pipeline_manifest


def test_write_pipeline_manifest_hashes_outputs(tmp_path: Path) -> None:
    data = tmp_path / "output" / "data"
    data.mkdir(parents=True)
    (data / "artifact.json").write_text("{}", encoding="utf-8")
    path = write_pipeline_manifest(tmp_path, render_status="pass", validation_status="pass")
    assert path.exists()
    assert "output/data/artifact.json" in path.read_text(encoding="utf-8")
