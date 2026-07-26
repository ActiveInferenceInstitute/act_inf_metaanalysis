"""Pure validation helpers for the dated tooling-source survey.

The registry is the authority for source pointers.  This module deliberately
does not contain a second hard-coded repository map: the external probe reads
the canonical URL and source kind from ``doc/tooling_inventory.yaml`` and this
module validates the resulting observations.
"""

from __future__ import annotations

from collections import Counter
from typing import Any

TOOLING_VERIFICATION_SCHEMA_VERSION = "2.0"

_REQUIRED_OBSERVATION_FIELDS = (
    "source_url",
    "source_kind",
    "source_alive",
    "release_or_version",
    "version_status",
    "license",
    "license_status",
    "activity_status",
    "status",
)


def build_tooling_verification_report(
    registry: dict[str, Any],
    observations: list[dict[str, Any]],
    *,
    checked_at: str,
) -> dict[str, Any]:
    """Validate and summarize one dated observation for every registry row.

    ``pass`` means that every retained row was probed and has the complete
    observation contract.  Row-level ``flagged`` statuses are retained as
    warnings for stale, source-only, restricted, or unlicensed projects; they
    are not hidden and do not become claims of software quality or maintenance.
    Probe failures, missing rows, and unknown rows remain release-blocking
    errors.
    """

    entries = registry.get("retained_tools", [])
    registry_ids = [str(entry.get("id", "")) for entry in entries]
    by_id = {str(item.get("id", "")): item for item in observations}
    results: list[dict[str, Any]] = []
    errors: list[str] = []

    for entry in entries:
        tool_id = str(entry.get("id", ""))
        observation = dict(by_id.get(tool_id, {}))
        if not observation:
            errors.append(f"missing observations for: {tool_id}")
        missing_fields = [
            field for field in _REQUIRED_OBSERVATION_FIELDS if field not in observation
        ]
        if missing_fields:
            errors.append(
                f"{tool_id}: incomplete observation fields: {', '.join(missing_fields)}"
            )
        if observation.get("probe_status") == "failed" or observation.get("source_alive") is False:
            errors.append(f"{tool_id}: source probe did not establish reachability")
        results.append(
            {
                "id": tool_id,
                "display_name": entry.get("display_name", tool_id),
                "evidence": entry.get("evidence"),
                "evidence_type": entry.get("evidence_type"),
                "verification_source": entry.get("verification_source", {}),
                **observation,
                "status": observation.get("status", "flagged"),
            }
        )

    missing_ids = sorted(set(registry_ids) - set(by_id))
    unknown_ids = sorted(set(by_id) - set(registry_ids))
    if missing_ids:
        errors.append(f"missing observations for: {', '.join(missing_ids)}")
    if unknown_ids:
        errors.append(f"observations for unknown tools: {', '.join(unknown_ids)}")

    counts = Counter(item["status"] for item in results)
    warnings = [
        f"{item['id']}: {', '.join(item.get('flags', []))}"
        for item in results
        if item.get("flags")
    ]
    repository_rows = [
        item for item in results if item.get("verification_tier") == "repository"
    ]
    source_only_rows = [
        item for item in results if item.get("verification_tier") == "source_only"
    ]
    explicit_license_rows = [
        item
        for item in results
        if item.get("license_status") in {"explicit", "declared_readme"}
    ]
    return {
        "schema_version": TOOLING_VERIFICATION_SCHEMA_VERSION,
        "checked_at": checked_at,
        "status": "pass" if not errors else "fail",
        "verification_complete": not errors,
        "errors": sorted(set(errors)),
        "warnings": warnings,
        "registry_count": len(entries),
        "verified_count": counts.get("verified", 0),
        "flagged_count": counts.get("flagged", 0),
        "repository_count": len(repository_rows),
        "source_only_count": len(source_only_rows),
        "explicit_license_count": len(explicit_license_rows),
        "results": results,
    }


__all__ = [
    "TOOLING_VERIFICATION_SCHEMA_VERSION",
    "build_tooling_verification_report",
]
