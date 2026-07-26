"""Reproducibility manifest for the regenerated publication package."""

from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from config import (
    DEFAULT_COMPLETE_YEAR_POLICY,
    DEFAULT_SEED,
    DEFAULT_TOPIC_STABILITY_SEEDS,
    PIPELINE_VERSION,
    PROMPT_VERSION,
)
from config_loader import load_analysis_config, load_kg_config


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _load_yaml(path: Path) -> dict[str, Any]:
    """Load the project configuration without making manifest writing fragile."""
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    value = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    return value if isinstance(value, dict) else {}


def _single_provenance_value(value: Any, fallback: Any) -> Any:
    """Collapse a uniform provenance histogram to its canonical value.

    A non-uniform histogram is retained as a sorted list so the manifest cannot
    silently select one version from a mixed extraction run.
    """
    if isinstance(value, dict):
        if len(value) == 1:
            return next(iter(value))
        if value:
            return sorted(str(key) for key in value)
    return fallback


_MANUSCRIPT_GUIDANCE_FILES = {"AGENTS.md", "README.md", "SKILL.md", "SYNTAX.md"}


def write_pipeline_manifest(
    project_root: Path,
    *,
    render_status: str = "pending",
    validation_status: str = "pending",
) -> Path:
    """Write hashes and runtime identifiers for all current publication inputs."""
    output_dir = project_root / "output"
    files: dict[str, dict[str, int | str]] = {}
    for base in (
        output_dir / "data",
        output_dir / "figures",
        output_dir / "manuscript",
        output_dir / "reports",
        output_dir / "pdf",
        output_dir / "web",
        output_dir / "validation",
        output_dir / "release",
    ):
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            relative = path.relative_to(project_root).as_posix()
            if (
                path.is_file()
                and path.name != "pipeline_manifest.json"
                and relative != "output/reports/snapshot_inventory.json"
            ):
                files[relative] = {
                    "sha256": _sha256(path),
                    "size_bytes": path.stat().st_size,
                }
    try:
        commit = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=project_root,
            capture_output=True,
            text=True,
            check=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        commit = "unknown"

    coverage_path = output_dir / "data" / "extraction_coverage.json"
    coverage = json.loads(coverage_path.read_text(encoding="utf-8")) if coverage_path.exists() else {}
    state_path = output_dir / "data" / "extraction_state.json"
    state = json.loads(state_path.read_text(encoding="utf-8")) if state_path.exists() else {}
    provenance_path = output_dir / "reports" / "extraction_provenance_summary.json"
    provenance = json.loads(provenance_path.read_text(encoding="utf-8")) if provenance_path.exists() else {}
    contract_path = output_dir / "reports" / "artifact_contract.json"
    contract = json.loads(contract_path.read_text(encoding="utf-8")) if contract_path.exists() else {}
    preflight_path = output_dir / "reports" / "release_preflight.json"
    preflight = json.loads(preflight_path.read_text(encoding="utf-8")) if preflight_path.exists() else {}
    tooling_path = output_dir / "reports" / "tooling_verification.json"
    tooling = json.loads(tooling_path.read_text(encoding="utf-8")) if tooling_path.exists() else {}
    package_verification_path = output_dir / "reports" / "release_package_verification.json"
    package_verification = (
        json.loads(package_verification_path.read_text(encoding="utf-8"))
        if package_verification_path.exists()
        else {}
    )
    search_path = output_dir / "reports" / "search_provenance.json"
    search = json.loads(search_path.read_text(encoding="utf-8")) if search_path.exists() else {}
    corpus_path = output_dir / "data" / "corpus.jsonl"
    corpus_size = sum(1 for line in corpus_path.read_text(encoding="utf-8").splitlines() if line.strip()) if corpus_path.exists() else 0
    input_paths = [
        project_root / "manuscript" / "config.yaml",
        project_root / "manuscript" / "references.bib",
        corpus_path,
        project_root / "pyproject.toml",
        project_root / "uv.lock",
        project_root / "doc" / "tooling_inventory.yaml",
    ]
    input_paths.extend(
        path
        for path in sorted((project_root / "manuscript").glob("*.md"))
        if path.name not in _MANUSCRIPT_GUIDANCE_FILES
    )
    input_hashes = {
        str(path.relative_to(project_root)): {
            "sha256": _sha256(path),
            "size_bytes": path.stat().st_size,
        }
        for path in input_paths
        if path.exists()
    }
    figures_count = len(list((output_dir / "figures").glob("*.png")))
    manuscript_count = len(list((output_dir / "manuscript").glob("*.md")))
    config_path = project_root / "manuscript" / "config.yaml"
    config = _load_yaml(config_path)
    analysis_config = load_analysis_config(config_path)
    kg_config = load_kg_config(config_path)
    pipeline_config = config.get("project_config", {}).get("pipeline", {})
    configured_pipeline = pipeline_config.get("pipeline_version", PIPELINE_VERSION)
    configured_prompt = pipeline_config.get("prompt_version", PROMPT_VERSION)
    configured_model = kg_config.get("llm_model") or ""
    render_formats = {
        key: bool(config.get("render", {}).get("formats", {}).get(key))
        for key in ("pdf", "html", "slides", "docx", "epub")
    }
    latest_sources = search.get("latest_source_status", {})
    arxiv_events = [
        event for name, event in latest_sources.items()
        if str(name).lower().startswith("arxiv[")
    ]
    source_gate = {
        "arxiv": bool(arxiv_events) and all(bool(event.get("success")) for event in arxiv_events),
        "semantic_scholar": bool(latest_sources.get("Semantic Scholar", {}).get("success")),
        "openalex": bool(latest_sources.get("OpenAlex", {}).get("success")),
    }
    gate_results = {
        "render": render_status,
        "validation": validation_status,
        "artifact_contract": contract.get("status", "missing"),
        "release_preflight": preflight.get("status", "missing"),
        "tooling_verification": tooling.get("status", "missing"),
        "release_package_manifest": package_verification.get("status", "missing"),
        "extraction_coverage": bool(coverage)
        and state.get("status") == "complete"
        and not coverage.get("failed_papers", 0)
        and not coverage.get("unprocessed_papers", 0),
        "literature_sources": source_gate,
    }
    run_id = coverage.get("run_id") or state.get("run_id")
    observed_pipeline = _single_provenance_value(
        provenance.get("pipeline_versions"), configured_pipeline
    )
    observed_prompt = _single_provenance_value(
        provenance.get("prompt_versions"), configured_prompt
    )
    observed_model = _single_provenance_value(
        provenance.get("unique_models"), configured_model
    )
    payload: dict[str, Any] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "git_commit": commit,
        "pipeline_version": observed_pipeline,
        "prompt_version": observed_prompt,
        "model": observed_model,
        "run_id": run_id,
        "as_of_date": analysis_config.get("as_of_date"),
        "complete_year_policy": analysis_config.get(
            "complete_year_policy", DEFAULT_COMPLETE_YEAR_POLICY
        ),
        "configuration": {
            "pipeline_version": configured_pipeline,
            "prompt_version": configured_prompt,
            "model": configured_model,
            "n_topics": analysis_config.get("n_topics"),
            "seed": analysis_config.get("seed", DEFAULT_SEED),
            "topic_stability_seeds": list(
                analysis_config.get("topic_stability_seeds", DEFAULT_TOPIC_STABILITY_SEEDS)
            ),
            "as_of_date": analysis_config.get("as_of_date"),
            "complete_year_policy": analysis_config.get(
                "complete_year_policy", DEFAULT_COMPLETE_YEAR_POLICY
            ),
            "render_formats": render_formats,
        },
        "render_status": render_status,
        "validation_status": validation_status,
        "input_hashes": input_hashes,
        "output_hashes": files,
        "counts": {
            "corpus_size": corpus_size,
            "eligible_papers": coverage.get("eligible_papers", state.get("eligible_papers")),
            "processed_papers": coverage.get("processed_papers", state.get("processed_papers")),
            "failed_papers": coverage.get("failed_papers", state.get("failed_papers")),
            "unprocessed_papers": coverage.get("unprocessed_papers", state.get("unprocessed_papers")),
            "assertions": coverage.get("assertions", state.get("assertions")),
            "figures": figures_count,
            "manuscript_files": manuscript_count,
        },
        "gate_results": gate_results,
        "files": files,
    }
    path = output_dir / "reports" / "pipeline_manifest.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    return path


__all__ = ["write_pipeline_manifest"]
