#!/usr/bin/env python3
"""Probe retained tooling sources and write a dated, fail-closed report."""

from __future__ import annotations

import argparse
import os
import re
import subprocess
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

from analysis.tooling_verification import build_tooling_verification_report


def _load_yaml(path: Path) -> dict[str, Any]:
    import yaml

    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def _github_token() -> str | None:
    """Use an existing token when available, without writing it to reports."""
    for name in ("GITHUB_TOKEN", "GH_TOKEN"):
        value = os.environ.get(name)
        if value:
            return value
    try:
        result = subprocess.run(
            ["gh", "auth", "token"],
            capture_output=True,
            text=True,
            timeout=5,
            check=False,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    token = result.stdout.strip()
    return token or None


def _headers(token: str | None) -> dict[str, str]:
    headers = {
        "Accept": "application/vnd.github+json",
        "User-Agent": "act-inf-metaanalysis-tooling-audit/2.0",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def _first_version_from_text(text: str) -> str | None:
    patterns = (
        r"(?im)^\s*version\s*=\s*[\"']([^\"']+)[\"']",
        r"(?im)^\s*version\s*:\s*[\"']?([^\"'\s]+)",
    )
    for pattern in patterns:
        match = re.search(pattern, text)
        if match:
            return match.group(1)
    return None


def _license_from_root(
    session: requests.Session,
    *,
    api_root: str,
    payload: dict[str, Any],
    token: str | None,
    timeout: float,
) -> dict[str, Any]:
    metadata = payload.get("license") or {}
    spdx_id = metadata.get("spdx_id")
    if spdx_id and spdx_id != "NOASSERTION":
        return {
            "license": spdx_id,
            "license_status": "explicit",
            "license_source": f"{api_root}/license",
        }

    try:
        response = session.get(
            f"{api_root}/contents",
            headers=_headers(token),
            timeout=timeout,
        )
        response.raise_for_status()
        root = response.json()
    except (requests.RequestException, ValueError, TypeError):
        root = []

    if isinstance(root, list):
        license_file = next(
            (
                item
                for item in root
                if str(item.get("name", "")).lower()
                in {"license", "license.md", "license.txt", "copying", "copying.md"}
            ),
            None,
        )
        if license_file:
            text = ""
            download_url = license_file.get("download_url")
            if download_url:
                try:
                    text = session.get(download_url, timeout=timeout).text
                except requests.RequestException:
                    pass
            first_line = next(
                (line.strip() for line in text.splitlines() if line.strip()),
                "custom license",
            )
            return {
                "license": first_line[:120],
                "license_status": "explicit",
                "license_source": license_file.get("html_url") or download_url,
            }

        readme = next(
            (item for item in root if str(item.get("name", "")).lower() == "readme.md"),
            None,
        )
        if readme and readme.get("download_url"):
            try:
                text = session.get(readme["download_url"], timeout=timeout).text
            except requests.RequestException:
                text = ""
            badge = re.search(
                r"license[^\n]*(?:badge|shield)[^\n]*?(MIT|Apache[- ]2\.0|GPL[- ]?3(?:\.0)?|BSD)[^\n]*",
                text,
                re.I,
            )
            if badge:
                return {
                    "license": badge.group(1).upper().replace(" ", "-"),
                    "license_status": "declared_readme",
                    "license_source": readme.get("html_url") or readme.get("download_url"),
                }
    return {
        "license": None,
        "license_status": "missing",
        "license_source": None,
    }


def _github_observation(
    session: requests.Session,
    tool_id: str,
    source: dict[str, str],
    timeout: float,
    token: str | None,
) -> dict[str, Any]:
    canonical_url = source["url"].rstrip("/")
    repository = canonical_url.removeprefix("https://github.com/")
    api_root = f"https://api.github.com/repos/{repository}"
    observation: dict[str, Any] = {
        "id": tool_id,
        "source_url": canonical_url,
        "source_kind": "github",
        "verification_tier": "repository",
    }
    try:
        response = session.get(api_root, headers=_headers(token), timeout=timeout)
        observation["http_status"] = response.status_code
        response.raise_for_status()
        payload = response.json()
        canonical_repo_url = payload.get("html_url") or canonical_url
        observation.update(
            {
                "source_url": canonical_repo_url,
                "resolved_url": response.url,
                "source_alive": True,
                "repository": canonical_repo_url,
                "default_branch": payload.get("default_branch"),
                "archived": bool(payload.get("archived", False)),
                "pushed_at": payload.get("pushed_at"),
            }
        )
        pushed_at = payload.get("pushed_at")
        activity_status = "unknown"
        if pushed_at:
            pushed = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
            age_days = max(0, (datetime.now(timezone.utc) - pushed).days)
            activity_status = "active" if age_days <= 365 else "stale"
            observation["days_since_push"] = age_days
        observation["activity_status"] = activity_status
        observation.update(
            _license_from_root(
                session,
                api_root=api_root,
                payload=payload,
                token=token,
                timeout=timeout,
            )
        )

        release_or_version = None
        version_status = "no_release_or_tag"
        releases = session.get(
            f"{api_root}/releases/latest",
            headers=_headers(token),
            timeout=timeout,
        )
        if releases.status_code == 200:
            release_payload = releases.json()
            release_or_version = release_payload.get("tag_name")
            version_status = "release"
            observation["release_published_at"] = release_payload.get("published_at")
        elif releases.status_code not in {404, 410}:
            observation["release_probe_status"] = f"http_{releases.status_code}"

        tags = session.get(
            f"{api_root}/tags?per_page=1",
            headers=_headers(token),
            timeout=timeout,
        )
        if release_or_version is None and tags.status_code == 200:
            tag_payload = tags.json()
            if tag_payload:
                release_or_version = tag_payload[0].get("name")
                version_status = "tag"

        if release_or_version is None:
            root = session.get(
                f"{api_root}/contents",
                headers=_headers(token),
                timeout=timeout,
            )
            root_payload = root.json() if root.status_code == 200 else []
            if isinstance(root_payload, list):
                for item in root_payload:
                    name = str(item.get("name", "")).lower()
                    if name in {"pyproject.toml", "setup.cfg", "package.json", "project.toml"} and item.get("download_url"):
                        text = session.get(item["download_url"], timeout=timeout).text
                        release_or_version = _first_version_from_text(text)
                        if release_or_version:
                            version_status = "package_metadata"
                            break
        observation["release_or_version"] = release_or_version or "none published"
        observation["version_status"] = version_status

        flags: list[str] = []
        if observation.get("archived"):
            flags.append("archived")
        if activity_status == "stale":
            flags.append("no push in the last 365 days")
        if observation.get("license_status") == "missing":
            flags.append("license not located in repository metadata or root files")
        elif observation.get("license_status") == "declared_readme":
            flags.append("license declared by README badge; no root license file")
        if observation.get("release_or_version") == "none published":
            flags.append("no release or version metadata")
        if str(observation.get("license", "")).startswith("VERSES Academic"):
            flags.append("academic/nonprofit research license; not an unrestricted OSI license")
        observation["flags"] = flags
        observation["status"] = "verified" if not flags else "flagged"
    except (requests.RequestException, ValueError, TypeError) as exc:
        observation.update(
            {
                "source_alive": False,
                "release_or_version": "unavailable",
                "version_status": "probe_failed",
                "license": None,
                "license_status": "probe_failed",
                "activity_status": "probe_failed",
                "status": "flagged",
                "probe_status": "failed",
                "flags": [f"source probe failed: {type(exc).__name__}"],
                "error": str(exc),
            }
        )
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
        "verification_tier": "source_only",
        "license": None,
        "license_status": "not_applicable",
        "activity_status": "not_applicable",
        "release_or_version": "not_applicable",
        "version_status": "not_applicable",
    }
    try:
        response = session.get(source["url"], timeout=timeout, allow_redirects=True)
        observation.update(
            {
                "http_status": response.status_code,
                "resolved_url": response.url,
                "source_alive": response.ok,
                "status": "flagged",
                "flags": ["source only; no public repository distribution was assessed"],
            }
        )
        if response.ok:
            if source["kind"] == "official_site":
                version = re.search(r"\b(SPM\d+)\b", response.text)
                observation["release_or_version"] = version.group(1) if version else "site version not stated"
                observation["version_status"] = "site"
            else:
                revision = re.search(r"arXiv:\s*([0-9.]+)(v\d+)?", response.text, re.I)
                observation["release_or_version"] = (
                    revision.group(1) + (revision.group(2) or "")
                    if revision
                    else "paper revision not parsed"
                )
                observation["version_status"] = "paper_revision"
    except requests.RequestException as exc:
        observation.update(
            {
                "source_alive": False,
                "release_or_version": "unavailable",
                "version_status": "probe_failed",
                "license_status": "probe_failed",
                "activity_status": "probe_failed",
                "status": "flagged",
                "flags": [f"source probe failed: {type(exc).__name__}"],
                "probe_status": "failed",
                "error": str(exc),
            }
        )
    return observation


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify retained tooling sources.")
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--output", default="output/reports/tooling_verification.json")
    args = parser.parse_args()
    registry = _load_yaml(PROJECT_ROOT / "doc" / "tooling_inventory.yaml")
    output_path = PROJECT_ROOT / args.output
    session = requests.Session()
    token = _github_token()
    observations = []
    for entry in registry.get("retained_tools", []):
        tool_id = str(entry.get("id", ""))
        source = entry.get("verification_source")
        if not isinstance(source, dict) or not source.get("url") or not source.get("kind"):
            observations.append(
                {
                    "id": tool_id,
                    "status": "flagged",
                    "flags": ["no verification source"],
                }
            )
        elif source["kind"] == "github":
            observations.append(_github_observation(session, tool_id, source, args.timeout, token))
        else:
            observations.append(_web_observation(session, tool_id, source, args.timeout))
    report = build_tooling_verification_report(
        registry,
        observations,
        checked_at=datetime.now(timezone.utc).isoformat(),
    )
    report["source_map_count"] = sum(
        1
        for entry in registry.get("retained_tools", [])
        if isinstance(entry.get("verification_source"), dict)
    )
    report["report_path"] = args.output
    output_path.parent.mkdir(parents=True, exist_ok=True)
    import json

    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
