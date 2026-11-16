"""Exercise the real CLI without replacing its sampling or metrics code."""

from __future__ import annotations

import csv
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from knowledge_graph.nanopublication import Assertion, create_nanopub, serialize_nanopubs
from literature.corpus import Corpus
from literature.models import Paper

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "07_run_validation_study.py"


def _inputs(tmp_path: Path) -> tuple[Path, Path]:
    output = tmp_path / "output"
    data = output / "data"
    data.mkdir(parents=True)
    paper = Paper("Human-reviewed paper", "A free energy claim.", year=2020, doi="10.1/human")
    Corpus([paper]).save(data / "corpus.jsonl")
    serialize_nanopubs([
        create_nanopub(Assertion("a1", paper.canonical_id, "claim", "supports", "FEP_UNIVERSALITY"))
    ], data / "nanopublications.jsonl")
    sample = output / "validation" / "sample.csv"
    sample.parent.mkdir()
    return output, sample


def _annotate(sample: Path) -> None:
    rows = [
        {
            "assertion_id": "a1", "ref_triage": "supports", "pipeline_triage": "supports",
            "ref_evidence_status": "explicit_claim", "ref_evidence_type": "theoretical",
            "evidence_status": "explicit_claim", "evidence_type": "theoretical",
            "secondary_triage": "", "abstract_excerpt": "A free energy claim.",
        },
        {
            "assertion_id": "a2", "ref_triage": "contradicts", "pipeline_triage": "supports",
            "ref_evidence_status": "mentions", "ref_evidence_type": "none",
            "evidence_status": "mentions", "evidence_type": "none",
            "secondary_triage": "", "abstract_excerpt": "A different judgment.",
        },
    ]
    with sample.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def _run(output: Path, *, human: bool = True) -> subprocess.CompletedProcess[str]:
    environment = dict(os.environ)
    environment.pop("TEMPLATE_REPO_ROOT", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--output-dir", str(output)]
        + (["--no-auto-labels"] if human else []),
        cwd=output.parent, env=environment, text=True, capture_output=True, timeout=30,
    )


def test_human_labels_survive_and_both_reports_use_primary_annotations(tmp_path: Path):
    output, sample = _inputs(tmp_path)
    _annotate(sample)
    before = sample.read_bytes()
    result = _run(output)
    assert result.returncode == 0, result.stderr
    assert sample.read_bytes() == before
    report_path = output / "reports" / "validation_metrics.json"
    assert report_path.read_bytes() == (output / "data" / "validation_metrics.json").read_bytes()
    report = json.loads(report_path.read_text())
    assert report["reference_kind"] == "human"
    assert report["sample_size"] == 2
    assert report["kappa_interrule"] is None
    assert report["kappa_interannotator"] is None
    assert report["kappa_reference_pipeline"] == 0.0
    assert report["precision"] == 0.5
    assert report["recall"] == 1.0
    assert report["f1"] == pytest.approx(2 / 3)
    assert not (sample.parent / "labels_rule_reference.csv").exists()


def test_default_mode_refuses_to_replace_existing_annotations(tmp_path: Path):
    output, sample = _inputs(tmp_path)
    _annotate(sample)
    before = sample.read_bytes()
    result = _run(output, human=False)
    assert result.returncode != 0
    assert sample.read_bytes() == before
    assert not (output / "reports" / "validation_metrics.json").exists()


@pytest.mark.parametrize("content", [None, "", "ref_triage\nsupports\n", "ref_triage\ninvalid\n"])
def test_unusable_human_input_fails_without_replacing_it(tmp_path: Path, content: str | None):
    output, sample = _inputs(tmp_path)
    if content is not None:
        sample.write_text(content, encoding="utf-8")
    result = _run(output)
    assert result.returncode != 0
    if content is None:
        assert not sample.exists()
    else:
        assert sample.read_text() == content
    assert not (output / "reports" / "validation_metrics.json").exists()
    assert not (output / "data" / "validation_metrics.json").exists()


def test_default_mode_still_generates_rule_reference_metrics(tmp_path: Path):
    output, sample = _inputs(tmp_path)
    result = _run(output, human=False)
    assert result.returncode == 0, result.stderr
    with sample.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    assert rows[0]["ref_triage"] == ""
    report = json.loads((output / "reports" / "validation_metrics.json").read_text())
    assert report["reference_kind"] == "deterministic_rule_based"
    assert report["kappa_interrule"] is not None
    assert report["kappa_interannotator"] is None
    assert (sample.parent / "labels_rule_reference.csv").is_file()


def test_human_secondary_agreement_is_not_mislabeled_interrule(tmp_path: Path):
    output, sample = _inputs(tmp_path)
    _annotate(sample)
    with sample.open(newline="") as handle:
        rows = list(csv.DictReader(handle))
    rows[0]["secondary_triage"] = "supports"
    rows[1]["secondary_triage"] = "neutral"
    with sample.open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    before = sample.read_bytes()
    result = _run(output)
    assert result.returncode == 0, result.stderr
    assert sample.read_bytes() == before
    report = json.loads((output / "reports" / "validation_metrics.json").read_text())
    assert report["kappa_interrule"] is None
    assert report["kappa_interannotator"] == pytest.approx(1 / 3)
    assert report["secondary_sample_size"] == 2
