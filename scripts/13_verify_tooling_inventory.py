#!/usr/bin/env python3
"""Probe retained tooling sources and write a dated, fail-closed report."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

import requests

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

from analysis.tooling_verification import TOOLING_SOURCES, build_tooling_verification_report


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _github_observation(
    session: requests.Session,
    tool_id: str,
    source: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    url = source["url"]
    observation: dict[str, Any] = {
        "id": tool_id,
        "source_url": url.removeprefix("https://api.github.com/repos/"),
        "source_kind": source["kind"],
    }
    try:
        response = session.get(url, timeout=timeout)
        observation["http_status"] = response.status_code
        response.raise_for_status()
        payload = response.json()
        license_payload = payload.get("license") or {}
        license_id = license_payload.get("spdx_id") or license_payload.get("name")
        archived = bool(payload.get("archived", False))
        pushed_at = payload.get("pushed_at")
        activity_status = "unknown"
        if pushed_at:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            age_days = (datetime.now(timezone.utc) - pushed).days
            activity_status = "active" if age_days <= 365 else "stale"
            observation["days_since_push"] = age_days
        observation.update({
            "repository": payload.get("html_url"),
            "default_branch": payload.get("default_branch"),
            "archived": archived,
            "activity_status": activity_status,
            "pushed_at": pushed_at,
            "license": license_id,
            "license_status": "explicit" if license_id and license_id != "NOASSERTION" else "missing",
            "latest_release": None,
        })
        releases = session.get(f"{url}/releases/latest", timeout=timeout)
        if releases.status_code == 200:
            observation["latest_release"] = releases.json().get("tag_name")
        elif releases.status_code == 404:
            observation["release_status"] = "no_release"
        else:
            observation["release_status"] = f"http_{releases.status_code}"
        reasons = []
        if archived:
            reasons.append("archived")
        if activity_status == "stale":
            reasons.append("no push in the last 365 days")
        if observation["license_status"] != "explicit":
            reasons.append("license not explicit")
        observation["status"] = "verified" if not reasons else "flagged"
        observation["flags"] = reasons
    except (requests.RequestException, ValueError, TypeError) as exc:
        if "rate limit" in str(exc).lower() or "403" in str(exc):
            repository = url.removeprefix("https://api.github.com/repos/")
            html_url = f"https://github.com/{repository}"
            try:
                fallback = session.get(html_url, timeout=timeout)
                return {
                    **observation,
                    "source_alive": fallback.ok,
                    "resolved_url": fallback.url,
                    "status": "flagged",
                    "probe_status": "github_api_rate_limited",
                    "flags": [
                        "GitHub API rate-limited; repository page reachable but metadata not rechecked"
                    ],
                }
            except requests.RequestException:
                pass
        observation.update({
            "status": "flagged",
            "flags": [f"source probe failed: {type(exc).__name__}"],
            "error": str(exc),
        })
    return observation


def _web_observation(
    session: requests.Session,
    tool_id: str,
    source: dict[str, str],
    timeout: float,
) -> dict[str, Any]:
    observation: dict[str, Any] = {
        "id": tool_id,
        "source_url": source["url"],
        "source_kind": source["kind"],
        "license": None,
        "license_status": "not_assessed",
        "activity_status": "not_applicable",
    }
    try:
        response = session.get(source["url"], timeout=timeout, allow_redirects=True)
        observation.update({
            "http_status": response.status_code,
            "resolved_url": response.url,
            "source_alive": response.ok,
            "status": "flagged",
            "flags": ["paper/site source only; repository and license not independently verified"],
        })
    except requests.RequestException as exc:
        observation.update({
            "status": "flagged",
            "source_alive": False,
            "flags": [f"source probe failed: {type(exc).__name__}"],
            "error": str(exc),
        })
    return observation


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify retained tooling sources.")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output", default="output/reports/tooling_verification.json")
    args = parser.parse_args()
    registry = _load_yaml(PROJECT_ROOT / "doc" / "tooling_inventory.yaml")
    output_path = PROJECT_ROOT / args.output
    prior_report: dict[str, Any] = {}
    if output_path.exists():
        try:
            prior_report = json.loads(output_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            prior_report = {}
    prior_by_id = {
        str(item.get("id")): item
        for item in prior_report.get("results", [])
        if isinstance(item, dict)
    }
    session = requests.Session()
    session.headers.update({"User-Agent": "act-inf-metaanalysis-tooling-audit/1.0"})
    observations = []
    for entry in registry.get("retained_tools", []):
        tool_id = str(entry.get("id", ""))
        source = TOOLING_SOURCES.get(tool_id)
        if source is None:
            observations.append({"id": tool_id, "status": "flagged", "flags": ["no source mapping"]})
        elif source["kind"] == "github":
            observation = _github_observation(session, tool_id, source, args.timeout)
            prior = prior_by_id.get(tool_id)
            if (
                observation.get("http_status") == 403
                and prior
                and prior.get("http_status") == 200
            ):
                observation = {
                    **prior,
                    "probe_status": "cached_due_to_github_api_rate_limit",
                    "current_probe_at": datetime.now(timezone.utc).isoformat(),
                }
            observations.append(observation)
        else:
            observations.append(_web_observation(session, tool_id, source, args.timeout))
    report = build_tooling_verification_report(
        registry,
        observations,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )
    report["source_map_count"] = len(TOOLING_SOURCES)
    report["report_path"] = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
