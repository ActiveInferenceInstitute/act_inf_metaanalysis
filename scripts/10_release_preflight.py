#!/usr/bin/env python3
"""Run the non-LLM release preflight and stage a local data package."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

from analysis.artifact_contract import validate_artifacts
from analysis.release_package import (
    prepare_release_package,
    validate_release_metadata,
    verify_release_manifest,
)
from analysis.pipeline_manifest import write_pipeline_manifest


def _render_checks(output_dir: Path) -> dict[str, object]:
    expected = {
        "pdf": output_dir / "pdf" / "act_inf_metaanalysis_combined.pdf",
        "html": output_dir / "web" / "index.html",
    }
    missing = [name for name, path in expected.items() if not path.exists() or path.stat().st_size == 0]
    return {"status": "pass" if not missing else "fail", "missing": missing}


def _test_check(project_root: Path) -> dict[str, object]:
    command = [sys.executable, "-m", "pytest", "--cov=src", "--cov-fail-under=90", "-q"]
    completed = subprocess.run(command, cwd=project_root, capture_output=True, text=True)
    return {
        "status": "pass" if completed.returncode == 0 else "fail",
        "returncode": completed.returncode,
        "command": command,
        "stdout_tail": completed.stdout[-4000:],
        "stderr_tail": completed.stderr[-2000:],
    }


def _json_report_check(path: Path, *, label: str) -> dict[str, object]:
    """Load a prerequisite JSON gate without silently treating it as passed."""
    if not path.exists():
        return {"status": "fail", "error": f"{label} report is missing", "path": str(path)}
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "fail", "error": f"{label} report is unreadable: {exc}", "path": str(path)}
    status = report.get("status")
    return {
        "status": status if status in {"pass", "fail"} else "fail",
        "reported_status": status,
        "path": str(path),
        "errors": report.get("errors", []),
        "warnings": report.get("warnings", []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run release checks without LLM regeneration.")
    parser.add_argument("--skip-tests", action="store_true", help="Skip the pytest coverage gate.")
    args = parser.parse_args()
    output_dir = PROJECT_ROOT / "output"
    contract = validate_artifacts(output_dir, PROJECT_ROOT)
    rdf = prepare_release_package(output_dir, PROJECT_ROOT)
    package_directory = rdf.get("package_directory")
    package_manifest = (
        verify_release_manifest(PROJECT_ROOT / package_directory)
        if package_directory
        else {"status": "fail", "errors": ["release package was not staged"]}
    )
    metadata = validate_release_metadata(output_dir, PROJECT_ROOT)
    render = _render_checks(output_dir)
    tooling = _json_report_check(
        output_dir / "reports" / "tooling_verification.json",
        label="tooling verification",
    )
    tests = {"status": "skipped"} if args.skip_tests else _test_check(PROJECT_ROOT)
    checks = {
        "artifact_contract": contract,
        "rdf_package": rdf,
        "release_package_manifest": package_manifest,
        "metadata": metadata,
        "render": render,
        "tooling_verification": tooling,
        "tests": tests,
    }
    blocking = {
        name: result for name, result in checks.items()
        if result.get("status") != "pass"
    }
    report = {
        "status": "pass" if not blocking else "fail",
        "checks": checks,
        "blocking_checks": sorted(blocking),
        "llm_regeneration": "not_run",
    }
    report_path = output_dir / "reports" / "release_preflight.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    # The preflight and package steps write reports after Stage 09. Refresh the
    # manifest last so its output hashes describe the completed release surface.
    manifest_path = output_dir / "reports" / "pipeline_manifest.json"
    prior_manifest: dict[str, object] = {}
    if manifest_path.exists():
        try:
            prior_manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior_manifest = {}
    manifest_render_status = str(
        prior_manifest.get("render_status", "pass" if render["status"] == "pass" else "fail")
    )
    manifest_validation_status = str(prior_manifest.get("validation_status", "pending"))
    write_pipeline_manifest(
        PROJECT_ROOT,
        render_status=manifest_render_status,
        validation_status=manifest_validation_status,
    )
    print(report_path)
    for name in sorted(blocking):
        print(f"ERROR: release preflight failed: {name}", file=sys.stderr)
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
