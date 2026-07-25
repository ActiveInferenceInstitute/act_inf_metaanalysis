#!/usr/bin/env python3
"""Write the final reproducibility manifest."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

from analysis.pipeline_manifest import write_pipeline_manifest


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--render-status", default="pass")
    parser.add_argument("--validation-status", default="pass")
    args = parser.parse_args()
    path = write_pipeline_manifest(
        PROJECT_ROOT,
        render_status=args.render_status,
        validation_status=args.validation_status,
    )
    print(path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
