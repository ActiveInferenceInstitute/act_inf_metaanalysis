from __future__ import annotations

from analysis.tooling_verification import build_tooling_verification_report


def test_tooling_report_requires_all_registry_rows() -> None:
    registry = {
        "retained_tools": [
            {
                "id": "one",
                "display_name": "One",
                "verification_source": {"url": "https://github.com/example/one", "kind": "github"},
            }
        ]
    }
    report = build_tooling_verification_report(
        registry,
        [{
            "id": "one",
            "status": "verified",
            "source_url": "https://github.com/example/one",
            "source_kind": "github",
            "verification_tier": "repository",
            "source_alive": True,
            "release_or_version": "v1.0.0",
            "version_status": "release",
            "license": "MIT",
            "license_status": "explicit",
            "activity_status": "active",
        }],
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


def test_tooling_report_passes_with_explicit_row_flags() -> None:
    registry = {
        "retained_tools": [
            {
                "id": "paper",
                "display_name": "Paper",
                "verification_source": {"url": "https://arxiv.org/abs/1234.5678", "kind": "preprint"},
            }
        ]
    }
    report = build_tooling_verification_report(
        registry,
        [{
            "id": "paper",
            "status": "flagged",
            "source_url": "https://arxiv.org/abs/1234.5678",
            "source_kind": "preprint",
            "verification_tier": "source_only",
            "source_alive": True,
            "release_or_version": "1234.5678v1",
            "version_status": "paper_revision",
            "license": None,
            "license_status": "not_applicable",
            "activity_status": "not_applicable",
            "flags": ["source only"],
        }],
        checked_at="2026-07-25T00:00:00+00:00",
    )
    assert report["status"] == "pass"
    assert report["verification_complete"] is True
    assert report["source_only_count"] == 1
    assert report["warnings"] == ["paper: source only"]
