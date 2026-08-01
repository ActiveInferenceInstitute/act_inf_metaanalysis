"""Validate and stage the nanopublication release package."""

from __future__ import annotations

import hashlib
import json
import shutil
import re
from pathlib import Path
from typing import Any

from rdflib import Dataset, URIRef
from rdflib.namespace import RDF

from knowledge_graph.nanopublication import (
    AIF_NS,
    AIF_NANOPUB_BASE,
    DC_NS,
    NP_NS,
    PROV_NS,
    XSD_NS,
    deserialize_nanopubs,
)

PACKAGE_SCHEMA_VERSION = "1.0"


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _nanopub_uri(nanopub_id: str) -> str:
    return AIF_NANOPUB_BASE.rstrip("/") + "/" + nanopub_id.replace("nanopub:", "", 1)


def validate_rdf_package(output_dir: Path) -> dict[str, Any]:
    """Check JSONL/TriG parity, RDF parseability, namespaces, and provenance."""
    data_dir = output_dir / "data"
    jsonl_path = data_dir / "nanopublications.jsonl"
    trig_path = data_dir / "nanopublications.trig"
    errors: list[str] = []
    json_ids: set[str] = set()
    json_count = 0
    provenance_missing = 0
    provenance_invalid = 0
    provenance_values: dict[str, set[str]] = {
        "model_id": set(),
        "prompt_version": set(),
        "pipeline_version": set(),
        "run_id": set(),
    }
    required_provenance = {
        "paper_id",
        "model_id",
        "prompt_version",
        "pipeline_version",
        "run_id",
        "processing_date",
    }

    if not jsonl_path.exists():
        errors.append("missing nanopublications.jsonl")
    else:
        try:
            records = [obj for obj in deserialize_nanopubs(jsonl_path)]
            json_count = len(records)
            for obj in records:
                json_ids.add(obj.nanopub_id)
                if not obj.provenance:
                    provenance_missing += 1
                    continue
                missing = required_provenance - {
                    key for key, value in obj.provenance.items() if value not in (None, "")
                }
                if missing or obj.provenance.get("paper_id") != obj.assertion.paper_id:
                    provenance_invalid += 1
                for key in provenance_values:
                    value = obj.provenance.get(key)
                    if value not in (None, ""):
                        provenance_values[key].add(str(value))
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"nanopublications.jsonl is invalid: {exc}")

    rdf_ids: set[str] = set()
    triple_count = 0
    namespace_checks = {
        "nanopub": False,
        "prov": False,
        "dcterms": False,
        "xsd": False,
        "aif": False,
    }
    if not trig_path.exists():
        errors.append("missing nanopublications.trig")
    else:
        dataset = Dataset()
        try:
            dataset.parse(trig_path, format="trig")
            triple_count = len(dataset)
            namespace_text = "\n".join(
                f"{prefix}:{namespace}" for prefix, namespace in dataset.namespaces()
            )
            namespace_checks = {
                "nanopub": NP_NS in namespace_text,
                "prov": PROV_NS in namespace_text,
                "dcterms": DC_NS in namespace_text,
                "xsd": XSD_NS in namespace_text,
                "aif": AIF_NS in namespace_text,
            }
            nanopub_type = URIRef(NP_NS + "Nanopublication")
            for graph in dataset.graphs():
                for subject in graph.subjects(RDF.type, nanopub_type):
                    uri = str(subject)
                    if uri.startswith(AIF_NANOPUB_BASE):
                        rdf_ids.add("nanopub:" + uri.removeprefix(AIF_NANOPUB_BASE))
        except (OSError, ValueError, SyntaxError) as exc:
            errors.append(f"nanopublications.trig is not parseable: {exc}")

    if json_ids != rdf_ids:
        errors.append(
            "JSONL/TriG nanopublication IDs disagree "
            f"(jsonl={len(json_ids)}, rdf={len(rdf_ids)})"
        )
    if provenance_missing:
        errors.append(f"{provenance_missing} nanopublications lack provenance")
    if provenance_invalid:
        errors.append(
            f"{provenance_invalid} nanopublications have incomplete or mismatched provenance"
        )
    for key, values in provenance_values.items():
        if len(values) != 1:
            errors.append(f"nanopublication provenance is not consistent for {key}")
    for name, present in namespace_checks.items():
        if not present:
            errors.append(f"TriG namespace missing: {name}")

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "jsonl_count": json_count,
        "rdf_nanopub_count": len(rdf_ids),
        "rdf_triple_count": triple_count,
        "jsonl_sha256": _sha256(jsonl_path) if jsonl_path.exists() else None,
        "trig_sha256": _sha256(trig_path) if trig_path.exists() else None,
        "namespace_checks": namespace_checks,
        "provenance_fields": {
            key: sorted(values) for key, values in provenance_values.items()
        },
        "package_schema_version": PACKAGE_SCHEMA_VERSION,
        "namespace": AIF_NS,
    }


def prepare_release_package(output_dir: Path, project_root: Path) -> dict[str, Any]:
    """Stage a deterministic local package after RDF validation succeeds."""
    validation = validate_rdf_package(output_dir)
    report_path = output_dir / "reports" / "rdf_package_validation.json"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text(json.dumps(validation, indent=2, sort_keys=True), encoding="utf-8")
    if validation["status"] != "pass":
        return validation

    data_dir = output_dir / "data"
    temporal = _load_json(data_dir / "temporal_analysis.json")
    config = _load_yaml(project_root / "manuscript" / "config.yaml")
    snapshot = str(temporal.get("as_of_date", "undated"))
    package_dir = output_dir / "release" / f"nanopublications-{snapshot}"
    if package_dir.exists():
        # A partial or stale prior staging must not leak files into the new
        # manifest's hashes — clear it before re-staging (MIN-13).
        shutil.rmtree(package_dir)
    package_dir.mkdir(parents=True, exist_ok=True)
    source_paths = (
        data_dir / "nanopublications.jsonl",
        data_dir / "nanopublications.trig",
        output_dir / "reports" / "extraction_provenance_summary.json",
    )
    for source in source_paths:
        destination = package_dir / source.name
        shutil.copyfile(source, destination)

    license_name = config.get("metadata", {}).get("license", "CC-BY-4.0")
    repository = config.get("metadata", {}).get("repository", "")
    package_readme = (
        f"# Nanopublication package ({snapshot})\n\n"
        f"This package contains {validation['jsonl_count']:,} RDF-compatible nanopublications "
        f"from the Active Inference meta-analysis snapshot dated {snapshot}.\n\n"
        f"- JSONL and TriG are parity-checked by `rdf_package_validation.json`.\n"
        f"- Domain namespace: `{AIF_NS}`\n"
        f"- License: {license_name}\n"
        f"- Source repository: {repository}\n"
        "- Scores are evidence mapping and hypothesis triage, not scientific confirmation.\n"
    )
    (package_dir / "README.md").write_text(package_readme, encoding="utf-8")
    validation["package_directory"] = str(package_dir.relative_to(project_root))
    validation["package_manifest"] = str(
        (package_dir / "package_manifest.json").relative_to(project_root)
    )
    report_path.write_text(json.dumps(validation, indent=2, sort_keys=True), encoding="utf-8")
    shutil.copyfile(report_path, package_dir / report_path.name)
    files = {}
    for path in sorted(package_dir.iterdir()):
        if path.name == "package_manifest.json" or not path.is_file():
            continue
        files[path.name] = {"sha256": _sha256(path), "size_bytes": path.stat().st_size}
    manifest = {
        "package_schema_version": PACKAGE_SCHEMA_VERSION,
        "snapshot_date": snapshot,
        "license": license_name,
        "repository": repository,
        "namespace": AIF_NS,
        "nanopublication_count": validation["jsonl_count"],
        "files": files,
    }
    (package_dir / "package_manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8"
    )
    return validation


def verify_release_manifest(package_dir: Path) -> dict[str, Any]:
    """Verify every staged package file against its recorded hash and size.

    This is the local, download-equivalent check used before an external
    deposit.  It deliberately does not claim that a remote deposit exists;
    it proves that the staged bytes are internally self-consistent and that
    the JSONL count agrees with the package manifest.
    """
    manifest_path = package_dir / "package_manifest.json"
    errors: list[str] = []
    if not manifest_path.exists():
        return {
            "status": "fail",
            "errors": ["missing package_manifest.json"],
            "package_directory": str(package_dir),
        }
    try:
        manifest = _load_json(manifest_path)
    except (OSError, json.JSONDecodeError) as exc:
        return {
            "status": "fail",
            "errors": [f"invalid package_manifest.json: {exc}"],
            "package_directory": str(package_dir),
        }

    expected_files = manifest.get("files", {})
    actual_files = {
        path.name: path
        for path in package_dir.iterdir()
        if path.is_file() and path.name != manifest_path.name
    }
    if set(expected_files) != set(actual_files):
        errors.append(
            "package file inventory differs from manifest "
            f"(expected={sorted(expected_files)}, actual={sorted(actual_files)})"
        )
    for name, metadata in expected_files.items():
        path = actual_files.get(name)
        if path is None:
            continue
        if _sha256(path) != metadata.get("sha256"):
            errors.append(f"sha256 mismatch: {name}")
        if path.stat().st_size != metadata.get("size_bytes"):
            errors.append(f"size mismatch: {name}")

    jsonl_path = package_dir / "nanopublications.jsonl"
    if jsonl_path.exists():
        try:
            count = len(deserialize_nanopubs(jsonl_path))
            if count != manifest.get("nanopublication_count"):
                errors.append(
                    "nanopublication count differs from manifest "
                    f"(manifest={manifest.get('nanopublication_count')}, actual={count})"
                )
        except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
            errors.append(f"nanopublications.jsonl is invalid: {exc}")
    else:
        errors.append("missing nanopublications.jsonl")

    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "package_directory": str(package_dir),
        "manifest_file_count": len(expected_files),
        "actual_file_count": len(actual_files),
        "nanopublication_count": manifest.get("nanopublication_count"),
    }


def validate_release_metadata(output_dir: Path, project_root: Path) -> dict[str, Any]:
    """Check configuration, provenance, render policy, and release metadata parity."""
    errors: list[str] = []
    config = _load_yaml(project_root / "manuscript" / "config.yaml")
    project_cfg = config.get("project_config", {})
    pipeline_cfg = project_cfg.get("pipeline", {})
    metadata = config.get("metadata", {})
    analysis_cfg = config.get("analysis", {})
    render_cfg = config.get("render", {}).get("formats", {})
    data_dir = output_dir / "data"
    reports_dir = output_dir / "reports"
    temporal = _load_json(data_dir / "temporal_analysis.json") if (data_dir / "temporal_analysis.json").exists() else {}
    provenance = _load_json(reports_dir / "extraction_provenance_summary.json") if (reports_dir / "extraction_provenance_summary.json").exists() else {}
    variables_payload = _load_json(data_dir / "manuscript_variables.json") if (data_dir / "manuscript_variables.json").exists() else {}
    variables = variables_payload.get("variables", {})

    repository = str(metadata.get("repository", ""))
    if not repository or not re.match(r"^https://github\.com/[^/]+/[^/]+/?$", repository):
        errors.append("metadata.repository is missing or not a canonical GitHub URL")
    if not metadata.get("license"):
        errors.append("metadata.license is missing")
    configured_pipeline = str(pipeline_cfg.get("pipeline_version", ""))
    configured_prompt = str(pipeline_cfg.get("prompt_version", ""))
    observed_pipelines = set(provenance.get("pipeline_versions", {}))
    observed_prompts = set(provenance.get("prompt_versions", {}))
    if configured_pipeline and observed_pipelines and observed_pipelines != {configured_pipeline}:
        errors.append("pipeline version differs between config and provenance")
    if configured_prompt and observed_prompts and observed_prompts != {configured_prompt}:
        errors.append("prompt version differs between config and provenance")
    configured_as_of = str(analysis_cfg.get("as_of_date", ""))
    if configured_as_of and temporal.get("as_of_date") != configured_as_of:
        errors.append("analysis.as_of_date differs from temporal artifact")
    if variables and configured_as_of and variables.get("AS_OF_DATE") != configured_as_of:
        errors.append("AS_OF_DATE differs between config and manuscript variables")
    expected_formats = {"pdf": True, "html": True, "slides": False, "docx": False, "epub": False}
    if {key: bool(render_cfg.get(key)) for key in expected_formats} != expected_formats:
        errors.append("render formats do not match the PDF/HTML-only publication policy")
    zenodo_path = reports_dir / "zenodo_deposit_metadata.json"
    if zenodo_path.exists():
        zenodo = _load_json(zenodo_path)
        if config.get("publication", {}).get("doi") and zenodo.get("doi") != config["publication"]["doi"]:
            errors.append("Zenodo metadata DOI differs from manuscript configuration")
        if configured_pipeline and zenodo.get("version") != configured_pipeline:
            errors.append("Zenodo metadata version differs from pipeline configuration")
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists() and repository and repository not in pyproject.read_text(encoding="utf-8"):
        errors.append("metadata.repository is not present in pyproject project URLs")
    return {
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "repository": repository,
        "license": metadata.get("license", ""),
        "pipeline_version": configured_pipeline,
        "prompt_version": configured_prompt,
        "as_of_date": configured_as_of,
        "render_formats": {key: bool(render_cfg.get(key)) for key in expected_formats},
    }


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return data if isinstance(data, dict) else {}


__all__ = [
    "PACKAGE_SCHEMA_VERSION",
    "prepare_release_package",
    "validate_rdf_package",
    "validate_release_metadata",
    "verify_release_manifest",
]
