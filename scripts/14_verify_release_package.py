#!/usr/bin/env python3
"""Verify the staged nanopublication package before external deposit."""

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

from analysis.release_package import verify_release_manifest


def _default_package(output_dir: Path) -> Path | None:
    packages = sorted((output_dir / "release").glob("nanopublications-*/"))
    return packages[-1] if packages else None


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify a staged release package.")
    parser.add_argument("--package-dir", default=None)
    parser.add_argument("--output", default="output/reports/release_package_verification.json")
    args = parser.parse_args()
    package_dir = Path(args.package_dir) if args.package_dir else _default_package(PROJECT_ROOT / "output")
    if package_dir is None:
        report = {"status": "fail", "errors": ["no staged release package found"]}
    else:
        report = verify_release_manifest(package_dir)
    output_path = PROJECT_ROOT / args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
