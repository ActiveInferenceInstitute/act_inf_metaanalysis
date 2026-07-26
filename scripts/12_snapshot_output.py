#!/usr/bin/env python3
"""Inventory versioned output and optionally copy it to a new snapshot."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

from analysis.snapshot_manager import copy_snapshot, inventory_output, write_inventory


def main() -> int:
    parser = argparse.ArgumentParser(description="Inventory or snapshot versioned output.")
    parser.add_argument("--label", help="New single-directory snapshot label; never overwrites.")
    args = parser.parse_args()
    output_dir = PROJECT_ROOT / "output"
    inventory_path = write_inventory(output_dir)
    result = inventory_output(output_dir)
    result["inventory_path"] = str(inventory_path.relative_to(PROJECT_ROOT))
    if args.label:
        result["snapshot_path"] = str(copy_snapshot(output_dir, args.label).relative_to(PROJECT_ROOT))
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
