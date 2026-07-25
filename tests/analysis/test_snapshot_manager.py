from __future__ import annotations

import json
from pathlib import Path

import pytest

from analysis.snapshot_manager import copy_snapshot, inventory_output, write_inventory


def test_inventory_and_snapshot_are_safe(tmp_path: Path) -> None:
    output = tmp_path / "output"
    (output / "data").mkdir(parents=True)
    (output / "data" / "x.json").write_text("{}", encoding="utf-8")
    inventory = inventory_output(output)
    assert inventory["file_count"] == 1
    assert inventory["total_bytes"] == 2
    assert write_inventory(output).exists()
    report = write_inventory(output)
    inventory_again = json.loads(report.read_text(encoding="utf-8"))
    assert all(
        item["path"]
        not in {"reports/snapshot_inventory.json", "reports/pipeline_manifest.json"}
        for item in inventory_again["files"]
    )
    snapshot = copy_snapshot(output, "run1")
    assert (snapshot / "data" / "x.json").exists()
    with pytest.raises(FileExistsError):
        copy_snapshot(output, "run1")


def test_snapshot_label_rejects_paths(tmp_path: Path) -> None:
    with pytest.raises(ValueError):
        copy_snapshot(tmp_path / "output", "../bad")
