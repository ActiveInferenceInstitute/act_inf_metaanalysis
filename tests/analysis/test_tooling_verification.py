from __future__ import annotations

from analysis.tooling_verification import build_tooling_verification_report


def test_tooling_report_requires_all_registry_rows() -> None:
    registry = {"retained_tools": [{"id": "one", "display_name": "One"}]}
    report = build_tooling_verification_report(
        registry,
        [{"id": "one", "status": "verified", "license": "MIT"}],
        checked_at="2026-07-25T00:00:00+00:00",
    )
    assert report["status"] == "pass"
    assert report["verified_count"] == 1


def test_tooling_report_flags_missing_observations() -> None:
    registry = {
        "retained_tools": [
            {"id": "one", "display_name": "One"},
            {"id": "two", "display_name": "Two"},
        ]
    }
    report = build_tooling_verification_report(
        registry,
        [{"id": "one", "status": "flagged", "flags": ["no license"]}],
        checked_at="2026-07-25T00:00:00+00:00",
    )
    assert report["status"] == "fail"
    assert report["flagged_count"] == 2
    assert "missing observations for: two" in report["errors"]
