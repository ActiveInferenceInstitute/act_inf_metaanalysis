from __future__ import annotations

import csv
import json
from pathlib import Path

from analysis.pilot_protocol import prepare_pilot_queues
from literature.corpus import Corpus
from literature.models import Paper


def test_prepare_pilot_queues_is_deterministic_and_blank(tmp_path: Path) -> None:
    output = tmp_path / "output"
    data = output / "data"
    data.mkdir(parents=True)
    corpus = Corpus()
    corpus.add(Paper("PDF paper", "abstract", year=2024, doi="10.1/pdf", pdf_url="https://example.org/a.pdf"))
    corpus.add(Paper("No PDF", "abstract", year=2023, doi="10.1/no"))
    corpus.save(data / "corpus.jsonl")
    validation = output / "validation"
    validation.mkdir()
    with (validation / "sample.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=["assertion_id", "paper_id", "hypothesis_id", "pipeline_triage"])
        writer.writeheader()
        writer.writerow({"assertion_id": "a1", "paper_id": "doi:10.1/pdf", "hypothesis_id": "H1", "pipeline_triage": "supports"})
    first = prepare_pilot_queues(output, fulltext_size=1, human_size=1)
    second = prepare_pilot_queues(output, fulltext_size=1, human_size=1)
    assert first == second
    assert first["human_labels_present"] is False
    with (validation / "human_calibration_queue.csv").open(encoding="utf-8") as handle:
        row = next(csv.DictReader(handle))
    assert row["human_stance"] == ""
    assert json.loads((validation / "pilot_manifest.json").read_text())["primary_analysis_unchanged"]


def test_prepare_pilot_queues_requires_corpus(tmp_path: Path) -> None:
    try:
        prepare_pilot_queues(tmp_path / "output")
    except FileNotFoundError:
        pass
    else:
        raise AssertionError("missing corpus should fail")
