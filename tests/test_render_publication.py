"""Render real temporary manuscripts; no substitute Pandoc or TeX executables."""

from __future__ import annotations

import json
import os
import re
import shutil
import struct
import subprocess
import sys
import zlib
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest
import yaml

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "15_render_publication.py"
pytestmark = pytest.mark.slow


class Surface(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables: list[list[str]] = []
        self.in_table = 0
        self.images: list[str] = []
        self.ids: set[str] = set()
        self.citations: set[str] = set()
        self.text: list[str] = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if tag == "table":
            self.tables.append([])
            self.in_table += 1
        if tag == "img":
            self.images.append(attributes["src"])
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        self.citations.update(attributes.get("data-cites", "").split())

    def handle_endtag(self, tag):
        if tag == "table":
            self.in_table -= 1

    def handle_data(self, data):
        self.text.append(data)
        if self.in_table:
            self.tables[-1].append(data)


def _png() -> bytes:
    def chunk(kind: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))
    header = struct.pack(">IIBBBBB", 2, 2, 8, 2, 0, 0, 0)
    rows = (b"\x00" + b"\x20\x40\x80" * 2) * 2
    return b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", header) + chunk(b"IDAT", zlib.compress(rows)) + chunk(b"IEND", b"")


def _inputs(tmp_path: Path, *, pdf: bool = False) -> tuple[Path, Path, Path]:
    manuscript = tmp_path / "manuscript"
    inputs = tmp_path / "inputs"
    output = tmp_path / "external-render"
    manuscript.mkdir()
    (inputs / "data").mkdir(parents=True)
    (inputs / "figures").mkdir()
    (inputs / "data" / "manuscript_variables.json").write_text(json.dumps({"variables": {"VALUE": "43"}}))
    (inputs / "figures" / "result.png").write_bytes(_png())
    (inputs / "figures" / "figure_registry.json").write_text(json.dumps({"result": {"filename": "result.png"}}))
    (manuscript / "config.yaml").write_text(yaml.safe_dump({
        "paper": {"title": "Publication regression"},
        "authors": [{"name": "Regression Fixture"}],
        "publication": {"year": 2024}, "render": {"formats": {"pdf": pdf, "html": not pdf}},
    }))
    (manuscript / "preamble.md").write_text(
        "```latex\n\\usepackage{booktabs}\n\\usepackage{longtable}\n\\usepackage{graphicx}\n```\n"
    )
    (manuscript / "references.bib").write_text(
        "@article{Alpha2024, author={Alpha, Alice}, title={Original evidence}, journal={Journal}, year={2024}}\n"
    )
    (manuscript / "01_results.md").write_text(r"""# Results

A measured result of {{VALUE}} follows \citep{Alpha2024}.

\begin{table}[htbp]
\centering
\caption{A retained scientific table}
\begin{tabular}{ll}
\toprule
Metric & Value \\
\midrule
Observation & {{VALUE}} \\
\bottomrule
\end{tabular}
\end{table}

\begin{longtable}{ll}
\caption{A retained long table} \\
\toprule
Metric & Value \\
\midrule
Second observation & 17 \\
\bottomrule
\end{longtable}

\begin{figure}[htbp]
\centering
\includegraphics[width=0.4\linewidth]{figures/result.png}
\caption{A \textbf{visible} caption with \citep{Alpha2024}.}
\end{figure}

# References

\bibliography{references}
""")
    return manuscript, inputs, output


def _render(manuscript: Path, inputs: Path, output: Path, *, relative_output: bool = False):
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    output_argument = os.path.relpath(output, SCRIPT.parents[1]) if relative_output else str(output)
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--manuscript-dir", str(manuscript),
         "--input-root", str(inputs), "--output-root", output_argument],
        cwd=output.parent, env=environment, text=True, capture_output=True, timeout=120,
    )


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="requires installed Pandoc")
@pytest.mark.parametrize("relative_output", [False, True])
def test_html_retains_tables_citations_bibliography_and_external_assets(
    tmp_path: Path, relative_output: bool,
):
    manuscript, inputs, output = _inputs(tmp_path)
    result = _render(manuscript, inputs, output, relative_output=relative_output)
    assert result.returncode == 0, result.stderr
    receipt = json.loads((output / "reports" / "render_receipt.json").read_text())
    index = Path(receipt["html"])
    assert index == output / "web" / "index.html"
    surface = Surface()
    surface.feed(index.read_text())
    tables = [" ".join(" ".join(parts).split()) for parts in surface.tables]
    assert len(tables) == 2
    assert any("Observation" in text and "43" in text for text in tables)
    assert any("Second observation" in text and "17" in text for text in tables)
    assert "Alpha2024" in surface.citations
    assert "ref-Alpha2024" in surface.ids
    assert len(surface.images) == 1
    parsed = urlsplit(surface.images[0])
    assert not parsed.scheme and not parsed.netloc
    asset = (index.parent / unquote(parsed.path)).resolve()
    assert asset.is_relative_to(output)
    assert asset.read_bytes() == (inputs / "figures" / "result.png").read_bytes()
    assert "visible" in " ".join(surface.text)


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="requires installed Pandoc")
def test_html_expands_declared_manuscript_math_macros(tmp_path: Path):
    manuscript, inputs, output = _inputs(tmp_path)
    preamble = manuscript / "preamble.md"
    preamble.write_text(preamble.read_text().replace(
        "```\n", r"""\newcommand{\score}{\operatorname{score}}
\newcommand{\cagr}{\text{CAGR}}
\newcommand{\F}{\mathcal{F}}
\newcommand{\KL}{\mathrm{KL}}
\newcommand{\E}{\mathbb{E}}
\newcommand{\scoreH}[1]{\text{score}(H_{#1})}
```
""",
    ))
    source = manuscript / "01_results.md"
    source.write_text(source.read_text() + r"""

\[
\score(H) + \scoreH{1} + \cagr + \F + \KL + \E
\]
""")
    result = _render(manuscript, inputs, output)
    assert result.returncode == 0, result.stderr
    html = (output / "web" / "index.html").read_text()
    assert "<math" in html
    surface = Surface()
    surface.feed(html)
    text = " ".join(surface.text)
    assert "score" in text and "CAGR" in text and "KL" in text
    assert not any(command in html for command in (r"\score", r"\cagr", r"\F", r"\KL", r"\E"))


@pytest.mark.skipif(shutil.which("pandoc") is None, reason="requires installed Pandoc")
def test_html_missing_bibliographic_key_does_not_publish_success(tmp_path: Path):
    manuscript, inputs, output = _inputs(tmp_path)
    source = manuscript / "01_results.md"
    source.write_text(source.read_text().replace("Alpha2024", "Missing2024"))
    result = _render(manuscript, inputs, output)
    assert result.returncode != 0
    assert not (output / "reports" / "render_receipt.json").exists()


@pytest.mark.skipif(
    any(shutil.which(tool) is None for tool in ("pandoc", "xelatex", "bibtex", "pdftotext")),
    reason="requires installed Pandoc, XeLaTeX, BibTeX and pdftotext",
)
def test_repeated_pdf_render_refreshes_citations_and_bibliography(tmp_path: Path):
    manuscript, inputs, output = _inputs(tmp_path, pdf=True)
    first = _render(manuscript, inputs, output)
    assert first.returncode == 0, first.stderr
    pdf = output / "pdf" / "act_inf_metaanalysis_combined.pdf"

    def text() -> str:
        result = subprocess.run(
            ["pdftotext", str(pdf), "-"], text=True, capture_output=True, timeout=20, check=True,
        )
        assert "# Results" not in result.stdout
        assert not re.search(r"(?m)^\s*[{}]\s*$", result.stdout)
        return " ".join(result.stdout.split())

    assert "Original evidence" in text()
    bibliography = manuscript / "references.bib"
    bibliography.write_text(
        bibliography.read_text().replace("Original evidence", "Revised evidence")
        + "@article{Beta2025, author={Beta, Bob}, title={Additional evidence}, journal={Journal}, year={2025}}\n"
    )
    source = manuscript / "01_results.md"
    source.write_text(source.read_text().replace(r"\citep{Alpha2024}", r"\citep{Alpha2024,Beta2025}"))
    second = _render(manuscript, inputs, output)
    assert second.returncode == 0, second.stderr
    rendered = text()
    assert "Revised evidence" in rendered
    assert "Additional evidence" in rendered
    assert "Original evidence" not in rendered
    assert Path(json.loads((output / "reports" / "render_receipt.json").read_text())["pdf"]) == pdf
