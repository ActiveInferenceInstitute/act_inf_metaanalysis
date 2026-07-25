"""Safe, explicit inventory and snapshot operations for disposable outputs."""

from __future__ import annotations

import json
import shutil
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def inventory_output(output_dir: Path) -> dict[str, Any]:
    """Return deterministic counts and sizes without self-referential metadata.

    The inventory and pipeline manifests are deliberately excluded from the
    file list. This removes the metadata feedback loop and makes repeated
    inventory/manifest runs idempotent.
    """
    files: list[dict[str, Any]] = []
    for path in sorted(output_dir.rglob("*")) if output_dir.exists() else []:
        relative = path.relative_to(output_dir).as_posix()
        if path.is_file() and relative not in {
            "reports/snapshot_inventory.json",
            "reports/pipeline_manifest.json",
        }:
            files.append({
                "path": str(path.relative_to(output_dir)),
                "size_bytes": path.stat().st_size,
            })
    snapshots_dir = output_dir / "snapshots"
    snapshots = sorted(path.name for path in snapshots_dir.iterdir()) if snapshots_dir.exists() else []
    return {
        "output_dir": str(output_dir),
        "file_count": len(files),
        "total_bytes": sum(item["size_bytes"] for item in files),
        "snapshots": snapshots,
        "files": files,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def write_inventory(output_dir: Path) -> Path:
    """Write the current output inventory report."""
    report = inventory_output(output_dir)
    path = output_dir / "reports" / "snapshot_inventory.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    return path


def copy_snapshot(output_dir: Path, label: str) -> Path:
    """Copy output to a new snapshot label; never overwrite an existing snapshot."""
    if not label or label in {".", ".."} or "/" in label or "\\" in label:
        raise ValueError("snapshot label must be a non-empty single directory name")
    destination = output_dir / "snapshots" / label
    if destination.exists():
        raise FileExistsError(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(output_dir, destination, ignore=shutil.ignore_patterns("snapshots"))
    return destination


__all__ = ["copy_snapshot", "inventory_output", "write_inventory"]
