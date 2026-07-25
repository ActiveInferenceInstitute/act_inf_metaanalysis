#!/usr/bin/env python3
"""Prepare reproducible full-text and human-calibration review queues."""

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

from analysis.pilot_protocol import prepare_pilot_queues


def main() -> int:
    parser = argparse.ArgumentParser(description="Prepare non-fabricated review queues.")
    parser.add_argument("--fulltext-size", type=int, default=100)
    parser.add_argument("--human-size", type=int, default=200)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    manifest = prepare_pilot_queues(
        PROJECT_ROOT / "output",
        fulltext_size=args.fulltext_size,
        human_size=args.human_size,
        seed=args.seed,
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
