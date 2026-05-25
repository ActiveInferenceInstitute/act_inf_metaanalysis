"""Tests for visualization.figure_runner."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from visualization.figure_runner import generate_all_figures


def test_generate_all_figures_minimal(tmp_path: Path) -> None:
    input_dir = tmp_path / "input"
    output_dir = tmp_path / "figures"
    input_dir.mkdir()
    with open(input_dir / "subfield_classification.json", "w", encoding="utf-8") as handle:
        json.dump({"A1_formal": 5, "B_tools": 3}, handle)
    with open(input_dir / "temporal_analysis.json", "w", encoding="utf-8") as handle:
        json.dump(
            {
                "year_counts": {"2020": 3, "2021": 5},
                "cumulative": {"2020": 3, "2021": 8},
                "smoothed_annual": {"2020": 3.0, "2021": 4.0},
            },
            handle,
        )
    with open(input_dir / "hypothesis_scores.json", "w", encoding="utf-8") as handle:
        json.dump({"FEP_UNIVERSALITY": 0.5}, handle)

    args = argparse.Namespace(input_dir=str(input_dir), output_dir=str(output_dir), dpi=100)
    paths = generate_all_figures(args)
    assert len(paths) >= 2
    assert output_dir.exists()
