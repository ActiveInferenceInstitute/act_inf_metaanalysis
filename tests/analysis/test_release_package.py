from __future__ import annotations

import json
from pathlib import Path

from analysis.release_package import (
    prepare_release_package,
    validate_release_metadata,
    validate_rdf_package,
    verify_release_manifest,
)
from knowledge_graph.nanopublication import (
    Assertion,
    create_nanopub,
    serialize_nanopubs,
    serialize_nanopubs_to_trig,
)
from knowledge_graph.provenance import ExtractionProvenance, write_provenance_summary


def _write_package_inputs(root: Path) -> None:
    data = root / "output" / "data"
    reports = root / "output" / "reports"
    data.mkdir(parents=True)
    reports.mkdir(parents=True)
    np_obj = create_nanopub(
        Assertion("a1", "doi:1", "claim", "supports", "FEP_UNIVERSALITY"),
        attribution="test",
        provenance=ExtractionProvenance.create(
            paper_id="doi:1", source_passage="abstract", model_id="gemma3:4b",
            llm_url="http://localhost:11435", pipeline_version="2.0.6",
            prompt_version="v2.0.6", run_id="run1",
        ).to_dict(),
    )
    serialize_nanopubs([np_obj], data / "nanopublications.jsonl")
    serialize_nanopubs_to_trig([np_obj], data / "nanopublications.trig")
    write_provenance_summary(data / "nanopublications.jsonl", reports / "extraction_provenance_summary.json")
    (data / "temporal_analysis.json").write_text(json.dumps({"as_of_date": "2026-07-24"}), encoding="utf-8")
    (root / "manuscript").mkdir()
    (root / "manuscript" / "config.yaml").write_text(
        "metadata:\n  license: CC-BY-4.0\n  repository: https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis\n"
        "publication:\n  doi: 10.5281/zenodo.1\nanalysis:\n  as_of_date: '2026-07-24'\n"
        "project_config:\n  pipeline:\n    pipeline_version: '2.0.6'\n    prompt_version: 'v2.0.6'\n"
        "render:\n  formats:\n    pdf: true\n    html: true\n    slides: false\n    docx: false\n    epub: false\n",
        encoding="utf-8",
    )
    (root / "pyproject.toml").write_text(
        "[project.urls]\nHomepage = 'https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis'\n",
        encoding="utf-8",
    )
    (reports / "zenodo_deposit_metadata.json").write_text(
        json.dumps({"doi": "10.5281/zenodo.1", "version": "2.0.6"}), encoding="utf-8"
    )
    (root / "output" / "data" / "manuscript_variables.json").write_text(
        json.dumps({"variables": {"AS_OF_DATE": "2026-07-24"}}), encoding="utf-8"
    )


def test_validate_and_prepare_rdf_package(tmp_path: Path) -> None:
    _write_package_inputs(tmp_path)
    report = validate_rdf_package(tmp_path / "output")
    assert report["status"] == "pass", report["errors"]
    prepared = prepare_release_package(tmp_path / "output", tmp_path)
    assert prepared["status"] == "pass"
    assert (tmp_path / prepared["package_manifest"]).exists()
    package_dir = tmp_path / prepared["package_directory"]
    verified = verify_release_manifest(package_dir)
    assert verified["status"] == "pass", verified["errors"]


def test_verify_release_manifest_detects_tampering(tmp_path: Path) -> None:
    _write_package_inputs(tmp_path)
    prepared = prepare_release_package(tmp_path / "output", tmp_path)
    package_dir = tmp_path / prepared["package_directory"]
    (package_dir / "README.md").write_text("tampered", encoding="utf-8")
    verified = verify_release_manifest(package_dir)
    assert verified["status"] == "fail"
    assert "sha256 mismatch: README.md" in verified["errors"]


def test_validate_release_metadata(tmp_path: Path) -> None:
    _write_package_inputs(tmp_path)
    report = validate_release_metadata(tmp_path / "output", tmp_path)
    assert report["status"] == "pass", report["errors"]


def test_validate_rdf_package_detects_missing_trig(tmp_path: Path) -> None:
    data = tmp_path / "output" / "data"
    data.mkdir(parents=True)
    (data / "nanopublications.jsonl").write_text("", encoding="utf-8")
    report = validate_rdf_package(tmp_path / "output")
    assert report["status"] == "fail"
    assert "missing nanopublications.trig" in report["errors"]
