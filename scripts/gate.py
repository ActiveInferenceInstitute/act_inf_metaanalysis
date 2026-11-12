#!/usr/bin/env python3
"""Local gate arms for this repository.

`./run.sh <arm>` is the only supported entry point; this module holds the
canonical command for each arm so the GitHub workflow, the documentation and
the timing receipt all execute the same argv.

Arms are deliberately independent: a failure in one does not hide another's
result when they are run one at a time. `all` stops at the first failure.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import platform
import re
import subprocess
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOG_DIR = ROOT / ".gate-logs"
RECEIPT = ROOT / "docs" / "_generated" / "gate_arms.md"

# Arm -> exact argv. Keep each command identical to what CI invokes.
ARMS: dict[str, tuple[str, ...]] = {
    "lint": ("uv", "run", "ruff", "check", "src/", "scripts/", "tests/"),
    "types": ("uv", "run", "mypy", "src/"),
    "test-fast": ("uv", "run", "pytest", "tests/", "-m", "not slow", "-q"),
    "test-full": ("uv", "run", "pytest", "tests/", "--cov=src", "--cov-fail-under=90"),
    "docs": ("uv", "run", "python", "scripts/check_docs.py"),
    "gnn": ("uv", "run", "python", "scripts/gnn_conformance.py"),
    "render": (
        "uv",
        "run",
        "python",
        "scripts/15_render_publication.py",
        "--output-root",
        ".render-check",
    ),
}

DEFAULT_ARM = "test-fast"
ALL_ARMS = ("lint", "types", "test-full", "docs", "gnn", "render")
BENCH_ARMS = ("lint", "types", "test-fast", "test-full", "docs", "gnn", "render")

# Measured on this workstation before the gate was consolidated; kept here so
# the receipt records the transition instead of only the latest run.
BASELINE = {
    "measured": "2026-11-12",
    "host": "darwin arm64, Python 3.15.2, uv 0.13.7, pandoc 3.13, TeX Live 2026",
    "lint": (0.3, "ruff check src/ scripts/ tests/ (warm cache)"),
    "types": (9.5, "mypy src/ (warm cache)"),
    "test-fast": (None, "no fast selection existed; the only arm was the full suite"),
    "test-full": (81.5, "pytest --cov=src --cov-fail-under=90: 687 passed, 1 skipped, 90.08%"),
    "docs": (None, "no documentation check existed"),
    "gnn": (None, "CI-only job; no local arm or cached parser environment"),
    "render": (None, "no render command existed in the repository"),
}


def _display(name: str) -> str:
    return " ".join(ARMS[name])


def _run_argv(argv: tuple[str, ...], *, capture: bool = False) -> tuple[int, str]:
    env = dict(os.environ)
    env.setdefault("PYTHONUNBUFFERED", "1")
    completed = subprocess.run(
        argv,
        cwd=ROOT,
        env=env,
        text=True,
        capture_output=capture,
    )
    return completed.returncode, (completed.stdout or "") + (completed.stderr or "")


def _stream_arm(name: str) -> int:
    print(f"[gate] {name}: {' '.join(ARMS[name])}", flush=True)
    started = time.perf_counter()
    code, _ = _run_argv(ARMS[name])
    elapsed = time.perf_counter() - started
    print(f"[gate] {name}: exit {code} in {elapsed:.1f}s", flush=True)
    return code


def _json_receipt(log: str) -> dict | None:
    """Return the first complete JSON object printed in a log."""
    decoder = json.JSONDecoder()
    for index, char in enumerate(log):
        if char != "{":
            continue
        try:
            payload, _ = decoder.raw_decode(log[index:])
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            return payload
    return None


def _evidence(name: str, log: str) -> str:
    if name in {"test-fast", "test-full"}:
        match = re.search(r"(\d+) passed(?:, (\d+) skipped)?", log)
        coverage = re.search(r"Total coverage: ([\d.]+)%", log)
        if not match:
            return "no pytest summary"
        text = f"{match.group(1)} passed"
        if match.group(2):
            text += f", {match.group(2)} skipped"
        if coverage:
            text += f", {coverage.group(1)}% coverage"
        return text
    if name == "gnn":
        payload = _json_receipt(log)
        if payload is None or "gnn-version" not in payload:
            return "no conformance receipt"
        return (
            f"gnn {payload.get('gnn-version')}, {payload.get('parsed')} parsed, "
            f"{payload.get('type-checked')} type-checked, {payload.get('result')}"
        )
    if name == "render":
        payload = _json_receipt(log)
        if payload is None or "figures" not in payload:
            return "no render receipt"
        return (
            f"{payload.get('sections')} sections, {payload.get('figures')} figures, "
            f"PDF {payload.get('pdf_bytes', 0)} bytes, HTML {payload.get('html_bytes', 0)} bytes"
        )
    if name == "docs":
        match = re.search(r"(\d+) markdown files", log)
        return match.group(1) + " markdown files checked" if match else "completed"
    return "completed"


def _versions() -> dict[str, str]:
    versions = {
        "host": f"{platform.system().lower()} {platform.machine()}",
        "python": platform.python_version(),
        "date": _dt.datetime.now().astimezone().isoformat(timespec="seconds"),
    }
    for key, argv in {
        "uv": ("uv", "--version"),
        "pandoc": ("pandoc", "--version"),
    }.items():
        try:
            code, out = _run_argv(argv, capture=True)
        except FileNotFoundError:
            versions[key] = "not installed"
            continue
        versions[key] = out.splitlines()[0].strip() if code == 0 and out else "unavailable"
    return versions


def _write_receipt(rows: list[tuple[str, float, int, str]]) -> Path:
    versions = _versions()
    lines = [
        "# Gate arms — measured receipt",
        "",
        "<!-- generated by scripts/gate.py (./run.sh bench); do not hand-edit -->",
        "",
        "`./run.sh <arm>` is the single entry point; each arm runs the command in",
        "`scripts/gate.py`, which is also what `.github/workflows/ci.yml` invokes.",
        "Hosted GitHub Actions is billing-locked for this organization, so these",
        "local runs are the gate.",
        "",
        "## Latest measurement",
        "",
        f"- Date: {versions['date']}",
        f"- Host: {versions['host']}",
        f"- Python: {versions['python']}",
        f"- uv: {versions['uv']}",
        f"- pandoc: {versions['pandoc']}",
        "- Run by: `./run.sh bench`",
        "",
        "| Arm | Command | Wall time | Exit | Evidence |",
        "| --- | --- | ---: | ---: | --- |",
    ]
    for name, seconds, code, evidence in rows:
        lines.append(
            f"| `{name}` | `{_display(name)}` | {seconds:.1f}s | {code} | {evidence} |"
        )
    lines += [
        "",
        "## Baseline before consolidation",
        "",
        f"Measured {BASELINE['measured']} on {BASELINE['host']}.",
        "",
        "| Arm | Wall time | Notes |",
        "| --- | ---: | --- |",
    ]
    for name in BENCH_ARMS:
        seconds, note = BASELINE[name]
        wall = "—" if seconds is None else f"{seconds:.1f}s"
        lines.append(f"| `{name}` | {wall} | {note} |")
    lines.append("")
    RECEIPT.parent.mkdir(parents=True, exist_ok=True)
    RECEIPT.write_text("\n".join(lines), encoding="utf-8")
    return RECEIPT


def _bench() -> int:
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    rows: list[tuple[str, float, int, str]] = []
    failures = 0
    # `docs` validates links to the receipt this run writes, so measure every
    # other arm first, write a provisional receipt, then check the docs.
    order = [name for name in BENCH_ARMS if name != "docs"] + ["docs"]
    for name in order:
        if name == "docs":
            _write_receipt(rows + [("docs", 0.0, 0, "receipt written for this run")])
        log_path = LOG_DIR / f"{name}.log"
        print(f"[bench] {name}", flush=True)
        started = time.perf_counter()
        try:
            code, log = _run_argv(ARMS[name], capture=True)
        except FileNotFoundError as exc:
            code, log = 127, f"{exc}\n"
        elapsed = time.perf_counter() - started
        log_path.write_text(log, encoding="utf-8")
        failures += code != 0
        rows.append((name, elapsed, code, _evidence(name, log)))
        print(f"[bench] {name}: exit {code} in {elapsed:.1f}s", flush=True)
    receipt = _write_receipt(rows)
    print(f"[bench] wrote {receipt.relative_to(ROOT)}", flush=True)
    return 1 if failures else 0


def _list() -> None:
    print(f"default: {DEFAULT_ARM}")
    for name in ARMS:
        print(f"{name:10s} {' '.join(ARMS[name])}")
    print(f"{'all':10s} {', '.join(ALL_ARMS)}")
    print(f"{'bench':10s} time every arm and refresh {RECEIPT.relative_to(ROOT)}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run one local gate arm")
    parser.add_argument("arm", nargs="?", default=DEFAULT_ARM)
    args = parser.parse_args(argv)
    arm = args.arm

    if arm in {"--list", "list"}:
        _list()
        return 0
    if arm == "bench":
        return _bench()
    if arm == "all":
        for name in ALL_ARMS:
            code = _stream_arm(name)
            if code != 0:
                return code
        return 0
    if arm not in ARMS:
        parser.error(f"unknown arm {arm!r}; run ./run.sh --list")
    return _stream_arm(arm)


if __name__ == "__main__":
    raise SystemExit(main())
