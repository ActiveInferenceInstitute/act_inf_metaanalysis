"""One publication-source completion contract for gates and presentation."""

from __future__ import annotations

from typing import Any

REQUIRED_SOURCE_LABELS = {
    "arxiv": "arXiv",
    "semantic_scholar": "Semantic Scholar",
    "openalex": "OpenAlex",
}


def literature_source_status(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    """Aggregate every latest query event, independently of requested/skip flags."""
    latest = report.get("latest_source_status", {})
    statuses: dict[str, dict[str, Any]] = {}
    for source, label in REQUIRED_SOURCE_LABELS.items():
        events = (
            [event for name, event in latest.items() if str(name).lower().startswith("arxiv[")]
            if source == "arxiv"
            else [latest[label]] if label in latest else []
        )
        failures = [event for event in events if event.get("success") is not True]
        details = list(dict.fromkeys(
            str(event.get("error_type") or event.get("error") or "not completed")
            for event in failures
        ))
        statuses[source] = {
            "success": bool(events) and not failures,
            "error": "; ".join(details) if events else "not completed",
        }
    return statuses
