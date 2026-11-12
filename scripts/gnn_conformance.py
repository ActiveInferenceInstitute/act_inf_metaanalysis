#!/usr/bin/env python3
"""Run the pinned GNN conformance check with a cached parser environment.

The parsed sketches are documentation, not pipeline input. This script keeps
the pinned parser out of the project environment: it creates ``.gnn-env`` for
the revision recorded in ``.github/gnn-pin.json`` and reuses it until the pin
changes. Network access is needed only when that environment is created.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PIN_PATH = ROOT / ".github" / "gnn-pin.json"
ENV_DIR = ROOT / ".gnn-env"
MARKER = ENV_DIR / "pin-revision"
GNN_DEPENDENCIES = ("defusedxml", "psutil", "pyyaml")


def _pin() -> dict[str, str]:
    payload = json.loads(PIN_PATH.read_text(encoding="utf-8"))
    for key in ("repository", "revision"):
        if key not in payload:
            raise SystemExit(f"{PIN_PATH.name} is missing {key!r}")
    return payload


def _run(argv: list[str]) -> None:
    completed = subprocess.run(argv, cwd=ROOT)
    if completed.returncode != 0:
        raise SystemExit(f"command failed ({completed.returncode}): {' '.join(argv)}")


def _ensure_env(pin: dict[str, str]) -> Path:
    python = ENV_DIR / "bin" / "python"
    recorded = MARKER.read_text(encoding="utf-8").strip() if MARKER.exists() else ""
    if python.exists() and recorded == pin["revision"]:
        return python
    _run(["uv", "venv", "--clear", str(ENV_DIR), "--python", "3.12"])
    _run(["uv", "pip", "install", "--python", str(python), *GNN_DEPENDENCIES])
    _run(
        [
            "uv",
            "pip",
            "install",
            "--python",
            str(python),
            "--no-deps",
            f"generalized-notation-notation @ git+https://github.com/{pin['repository']}.git@{pin['revision']}",
        ]
    )
    MARKER.write_text(pin["revision"] + "\n", encoding="utf-8")
    return python


def main() -> int:
    pin = _pin()
    python = _ensure_env(pin)
    completed = subprocess.run(
        [str(python), "scripts/validate_gnn_conformance.py"],
        cwd=ROOT,
    )
    return completed.returncode


if __name__ == "__main__":
    sys.exit(main())
