#!/usr/bin/env python3
"""Validate the cross-stage publication artifact contract."""

from __future__ import annotations

import logging
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

from analysis.artifact_contract import validate_artifacts


def main() -> int:
    logging.basicConfig(level=logging.INFO)
    report = validate_artifacts(PROJECT_ROOT / "output", PROJECT_ROOT)
    print(PROJECT_ROOT / "output" / "reports" / "artifact_contract.json")
    if report["errors"]:
        for error in report["errors"]:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
