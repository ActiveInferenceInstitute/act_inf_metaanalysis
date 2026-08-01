from __future__ import annotations
from pathlib import Path
from visualization.temporal_plots import (
    _growth_annotation_text,
    _median_year,
    plot_growth_curve,
    plot_subfield_timeline,
)

class TestTemporalPlots:
    """Tests for temporal trend visualization functions."""

    YEAR_COUNTS = {2018: 5, 2019: 8, 2020: 12, 2021: 15, 2022: 22, 2023: 30}
    CUMULATIVE = {2018: 5, 2019: 13, 2020: 25, 2021: 40, 2022: 62, 2023: 92}

    def test_growth_annotation_contains_headline_values(self) -> None:
        """The CAGR/N/span annotation text carries the real values (MIN-15)."""
        text = _growth_annotation_text(
            total_n=93, dated_papers=92, undated_papers=1,
            cagr_pct=24.94, first_year=2018, span_end=2023,
            current_year_is_partial=False, as_of_date=None,
        )
        assert "N = 93" in text
        assert "Dated years = 92" in text
        assert "undated = 1" in text
        assert "CAGR = 24.9%" in text
        assert "Span: 2018–2023" in text
        assert "As of" not in text

    def test_growth_annotation_partial_year_and_as_of(self) -> None:
        """Partial-year and as-of flags appear in the annotation (MIN-15)."""
        text = _growth_annotation_text(
            total_n=100, dated_papers=99, undated_papers=0,
            cagr_pct=10.0, first_year=2020, span_end=2025,
            current_year_is_partial=True, as_of_date="2026-01-15",
        )
        assert "Hatched bar = current year YTD" in text
        assert "As of 2026-01-15" in text

    def test_median_year_weighted(self) -> None:
        """Median year is count-weighted (MIN-15)."""
        assert _median_year([2018, 2019, 2020], [1, 4, 1]) == 2019
        assert _median_year([2020], [5]) == 2020
        assert _median_year([], []) is None

    def test_plot_growth_curve_creates_file(self, tmp_path: Path) -> None:
        output = tmp_path / "growth_curve.png"
        result = plot_growth_curve(
            self.YEAR_COUNTS,
            self.CUMULATIVE,
            output,
            corpus_size=93,
            undated_papers=1,
        )
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0
        # Content validation: PIL check
        from PIL import Image
        img = Image.open(output)
        assert img.width > 0 and img.height > 0

    def test_plot_growth_curve_single_year(self, tmp_path: Path) -> None:
        output = tmp_path / "single_year.png"
        result = plot_growth_curve({2023: 10}, {2023: 10}, output)
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0
        # Content validation: PIL check
        from PIL import Image
        img = Image.open(output)
        assert img.width > 0 and img.height > 0

    def test_plot_growth_curve_explicit_cagr_and_as_of(self, tmp_path: Path) -> None:
        """Explicit CAGR, smoothed trendline, partial-year and as-of branches render (MIN-15)."""
        output = tmp_path / "gc_explicit.png"
        result = plot_growth_curve(
            self.YEAR_COUNTS,
            self.CUMULATIVE,
            output,
            smoothed_annual={y: c / 2 for y, c in self.YEAR_COUNTS.items()},
            current_year_is_partial=True,
            as_of_date="2026-07-26",
            cagr=0.24,
            cagr_end_year=2025,
            corpus_size=93,
            undated_papers=1,
        )
        assert result == output
        assert output.exists() and output.stat().st_size > 0

    def test_plot_subfield_timeline_creates_file(self, tmp_path: Path) -> None:
        subfield_data = {
            "A2_philosophy": {2018: 3, 2019: 5, 2020: 7, 2021: 8},
            "C1_neuroscience": {2018: 1, 2019: 2, 2020: 3, 2021: 5},
            "C2_robotics": {2018: 1, 2019: 1, 2020: 2, 2021: 2},
        }
        output = tmp_path / "subfield_timeline.png"
        result = plot_subfield_timeline(
            subfield_data,
            output,
            corpus_size=13,
            undated_papers=1,
        )
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0
        # Content validation: PIL check
        from PIL import Image
        img = Image.open(output)
        assert img.width > 0 and img.height > 0

    def test_plot_subfield_timeline_empty(self, tmp_path: Path) -> None:
        output = tmp_path / "empty_timeline.png"
        result = plot_subfield_timeline({}, output)
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0
        # Content validation: PIL check (empty plot still produces valid image)
        from PIL import Image
        img = Image.open(output)
        assert img.width > 0 and img.height > 0

    def test_plot_subfield_timeline_partial_year(self, tmp_path: Path) -> None:
        """Partial-year hatch + total-N annotation branch renders (MIN-15 coverage)."""
        subfield_data = {
            "A2_philosophy": {2020: 3, 2021: 5},
            "C1_neuroscience": {2020: 1, 2021: 2},
        }
        output = tmp_path / "timeline_partial.png"
        result = plot_subfield_timeline(
            subfield_data,
            output,
            corpus_size=11,
            undated_papers=0,
            current_year_is_partial=True,
            current_year=2021,
            as_of_date="2026-07-26",
        )
        assert result == output
        assert output.exists() and output.stat().st_size > 0

    def test_plot_subfield_timeline_all_eight(self, tmp_path: Path) -> None:
        subfield_data = {
            "A2_philosophy": {2020: 10, 2021: 12},
            "B_tools": {2020: 5, 2021: 8},
            "C2_robotics": {2020: 3, 2021: 4},
            "C1_neuroscience": {2020: 7, 2021: 9},
            "C4_psychiatry": {2020: 4, 2021: 5},
            "A1_formal": {2020: 2, 2021: 3},
            "C5_biology": {2020: 1, 2021: 2},
            "C3_language": {2020: 1, 2021: 2},
        }
        output = tmp_path / "all_subfields.png"
        result = plot_subfield_timeline(subfield_data, output)
        assert result == output
        assert output.exists()
        assert output.stat().st_size > 0
        # Content validation: PIL check
        from PIL import Image
        img = Image.open(output)
        assert img.width > 0 and img.height > 0
