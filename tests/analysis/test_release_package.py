from __future__ import annotations

import json
from pathlib import Path

import pytest
from rdflib import Dataset, Literal, URIRef

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
    (root / "docs" / "manuscript").mkdir(parents=True)
    (root / "docs" / "manuscript" / "config.yaml").write_text(
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


@pytest.mark.parametrize("field", ["claim", "evidence_quote", "assertion_type", "confidence", "provenance", "attribution", "created_date"])
def test_same_ids_cannot_hide_rdf_payload_changes(tmp_path: Path, field: str) -> None:
    from knowledge_graph.nanopublication import deserialize_nanopubs

    _write_package_inputs(tmp_path)
    data = tmp_path / "output" / "data"
    records = deserialize_nanopubs(data / "nanopublications.jsonl")
    record = records[0]
    if field == "provenance":
        assert record.provenance is not None
        record.provenance["model_id"] = "different-model"
    elif field == "confidence":
        record.assertion.confidence = 0.25
    elif field == "assertion_type":
        record.assertion.assertion_type = "contradicts"
    elif field in {"claim", "evidence_quote"}:
        setattr(record.assertion, field, "different evidence")
    elif field == "created_date":
        record.created_date = "2001-01-01T00:00:00+00:00"
    else:
        record.attribution = "different attribution"
    serialize_nanopubs_to_trig(records, data / "nanopublications.trig")
    report = validate_rdf_package(tmp_path / "output")
    assert report["jsonl_count"] == report["rdf_nanopub_count"] == 1
    assert report["status"] == "fail"
    assert any("graph content disagrees" in error for error in report["errors"])


@pytest.mark.parametrize("mutation", ["extra_graph", "move_triple", "head_link"])
def test_rdf_named_graph_structure_is_part_of_parity(tmp_path: Path, mutation: str) -> None:
    _write_package_inputs(tmp_path)
    trig = tmp_path / "output" / "data" / "nanopublications.trig"
    dataset = Dataset()
    dataset.parse(trig, format="trig")
    if mutation == "extra_graph":
        dataset.graph(URIRef("urn:unexpected")).add(
            (URIRef("urn:subject"), URIRef("urn:predicate"), Literal("extra"))
        )
    else:
        suffix = "#assertion" if mutation == "move_triple" else "#head"
        source = next(graph for graph in dataset.graphs() if str(graph.identifier).endswith(suffix))
        if mutation == "head_link":
            triple = next(source.triples((None, URIRef("http://www.nanopub.org/nschema#hasAssertion"), None)))
            source.remove(triple)
            source.add((triple[0], triple[1], URIRef("urn:wrong-assertion")))
        else:
            triple = next(iter(source))
            source.remove(triple)
            target = next(graph for graph in dataset.graphs() if str(graph.identifier).endswith("#provenance"))
            target.add(triple)
    dataset.serialize(destination=str(trig), format="trig")
    report = validate_rdf_package(tmp_path / "output")
    assert report["rdf_nanopub_count"] == report["jsonl_count"] == 1
    assert report["status"] == "fail"


def test_parity_accepts_reserialized_graphs_but_rejects_invalid_jsonl(tmp_path: Path) -> None:
    _write_package_inputs(tmp_path)
    data = tmp_path / "output" / "data"
    trig = data / "nanopublications.trig"
    dataset = Dataset()
    dataset.parse(trig, format="trig")
    dataset.bind("evidence", URIRef("http://activeinference.institute/ontology/"))
    dataset.serialize(destination=str(trig), format="trig")
    assert validate_rdf_package(tmp_path / "output")["status"] == "pass"
    with (data / "nanopublications.jsonl").open("a") as handle:
        handle.write("{invalid json}\n")
    assert validate_rdf_package(tmp_path / "output")["status"] == "fail"


def test_failed_semantic_parity_preserves_existing_staged_package(tmp_path: Path) -> None:
    _write_package_inputs(tmp_path)
    prepared = prepare_release_package(tmp_path / "output", tmp_path)
    package = tmp_path / prepared["package_directory"]
    before = {path.relative_to(package): path.read_bytes() for path in package.rglob("*") if path.is_file()}
    jsonl = tmp_path / "output" / "data" / "nanopublications.jsonl"
    row = json.loads(jsonl.read_text())
    row["assertion"]["confidence"] = 0.125
    jsonl.write_text(json.dumps(row) + "\n")
    assert prepare_release_package(tmp_path / "output", tmp_path)["status"] == "fail"
    assert {path.relative_to(package): path.read_bytes() for path in package.rglob("*") if path.is_file()} == before
