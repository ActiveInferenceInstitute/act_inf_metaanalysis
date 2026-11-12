#!/usr/bin/env python3
"""Render the manuscript to PDF and HTML from declared variables.

Inputs (all required, no silent fallbacks):

- ``manuscript/config.yaml`` — title, subtitle, authors, DOI, render formats.
- ``manuscript/*.md`` — pandoc Markdown sections, ordered by numeric prefix.
- ``manuscript/preamble.md`` — a fenced ``latex`` block used as the LaTeX header.
- ``output/data/manuscript_variables.json`` — the declared variable map written
  by ``scripts/z_generate_manuscript_variables.py``.
- ``output/figures/figure_registry.json`` plus the generated PNGs.

The script fails when a variable, figure, or tool is missing; it never renders
blank text or partial output. PDF rendering uses pandoc -> XeLaTeX -> BibTeX ->
XeLaTeX, the same toolchain the published artifacts were built with.
"""

from __future__ import annotations

import argparse
import html
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

import yaml  # noqa: E402

from manuscript.variables import TOKEN_RE, inject_variables  # noqa: E402

EXCLUDED_SECTIONS = {"AGENTS.md", "README.md", "SKILL.md", "SYNTAX.md", "preamble.md"}
SECTION_RE = re.compile(r"^(\d{2}[a-z]?)_")
INCLUDE_RE = re.compile(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}")
FIGURE_ENV_RE = re.compile(r"\\begin\{figure\}(?:\[[^\]]*\])?(.*?)\\end\{figure\}", re.S)
CAPTION_RE = re.compile(r"\\caption\{")


class RenderError(SystemExit):
    """Raised when the render cannot produce an honest artifact."""


def _fail(message: str) -> None:
    raise RenderError(f"render: {message}")


def _load_yaml(path: Path) -> dict:
    if not path.exists():
        _fail(f"missing configuration file: {path}")
    with path.open(encoding="utf-8") as handle:
        return yaml.safe_load(handle) or {}


def load_variables(output_root: Path) -> dict[str, str]:
    path = output_root / "data" / "manuscript_variables.json"
    if not path.exists():
        _fail(
            f"missing declared variables file: {path} "
            "(run scripts/z_generate_manuscript_variables.py first)"
        )
    payload = json.loads(path.read_text(encoding="utf-8"))
    variables = payload.get("variables")
    if not isinstance(variables, dict) or not variables:
        _fail(f"{path} does not contain a non-empty 'variables' mapping")
    non_string = sorted(key for key, value in variables.items() if not isinstance(value, str))
    if non_string:
        _fail(f"{path} has non-string values for: {', '.join(non_string)}")
    return variables


def section_files(manuscript_dir: Path) -> list[Path]:
    files = [
        path
        for path in sorted(manuscript_dir.glob("*.md"))
        if path.name not in EXCLUDED_SECTIONS and SECTION_RE.match(path.name)
    ]
    if not files:
        _fail(f"no numbered manuscript sections found in {manuscript_dir}")
    return files


def hydrate_sections(files: list[Path], variables: dict[str, str]) -> list[tuple[str, str]]:
    sections: list[tuple[str, str]] = []
    for path in files:
        rendered = inject_variables(path.read_text(encoding="utf-8"), variables, filename=path.name)
        unresolved = sorted(set(TOKEN_RE.findall(rendered)))
        if unresolved:
            _fail(f"{path.name} has undeclared variables: {', '.join(unresolved)}")
        sections.append((path.name, rendered.rstrip() + "\n"))
    return sections


def preamble_tex(manuscript_dir: Path) -> str:
    path = manuscript_dir / "preamble.md"
    if not path.exists():
        _fail(f"missing LaTeX preamble: {path}")
    match = re.search(r"^```latex\s*$\n(.*?)^```\s*$", path.read_text(encoding="utf-8"), re.S | re.M)
    if not match:
        _fail(f"{path} has no fenced 'latex' block")
    return match.group(1)


def load_figure_registry(figures_dir: Path) -> dict[str, str]:
    path = figures_dir / "figure_registry.json"
    if not path.exists():
        _fail(f"missing figure registry: {path}")
    registry = json.loads(path.read_text(encoding="utf-8"))
    filenames: dict[str, str] = {}
    for label, entry in registry.items():
        filename = entry.get("filename")
        if not filename:
            _fail(f"figure registry entry {label!r} has no filename")
        target = figures_dir / filename
        if not target.is_file() or target.stat().st_size == 0:
            _fail(f"registered figure {label!r} is missing or empty: {target}")
        filenames[filename] = label
    return filenames


def validate_figures(text: str, figures_dir: Path, registry: dict[str, str]) -> list[str]:
    referenced: list[str] = []
    for include in INCLUDE_RE.findall(text):
        filename = Path(include).name
        target = figures_dir / filename
        if not target.is_file() or target.stat().st_size == 0:
            _fail(f"manuscript includes a missing or empty figure: {include}")
        if filename not in registry:
            _fail(f"manuscript includes an unregistered figure: {filename}")
        referenced.append(filename)
    if not referenced:
        _fail("manuscript includes no figures, so the figure registry cannot be validated")
    return sorted(set(referenced))


def _tex_escape(value: str) -> str:
    replacements = {
        "\\": r"\textbackslash{}",
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
    }
    return "".join(replacements.get(char, char) for char in value)


def title_block(config: dict) -> str:
    paper = config.get("paper", {})
    title = paper.get("title")
    subtitle = paper.get("subtitle", "")
    authors = config.get("authors", [])
    publication = config.get("publication", {})
    if not title or not authors:
        _fail("config.yaml must declare paper.title and at least one author")
    lines = ["\\begin{center}", f"{{\\LARGE\\bfseries {_tex_escape(title)}\\par}}"]
    if subtitle:
        lines += ["\\vspace{0.6em}", f"{{\\large {_tex_escape(subtitle)}\\par}}"]
    lines += ["\\vspace{1.4em}"]
    rendered_authors = []
    for author in authors:
        parts = [f"{_tex_escape(str(author.get('name', '')))}\\\\"]
        for affiliation in author.get("affiliations", []):
            parts.append(f"\\footnotesize{{{_tex_escape(str(affiliation))}}}\\\\")
        if author.get("email"):
            parts.append(f"\\footnotesize{{\\texttt{{{_tex_escape(str(author['email']))}}}}}\\\\")
        if author.get("orcid"):
            orcid = _tex_escape(str(author["orcid"]))
            parts.append(
                "\\footnotesize{\\href{https://orcid.org/" + orcid + "}{ORCID: " + orcid + "}}"
            )
        rendered_authors.append("\\begin{tabular}[t]{c}" + "\n".join(parts) + "\\end{tabular}")
    lines.append(" \\and ".join(rendered_authors))
    lines.append("\\vspace{1.2em}")
    date = str(publication.get("year", ""))
    if date:
        lines.append(f"{{\\large {_tex_escape(date)}\\par}}")
    if publication.get("doi"):
        doi = str(publication["doi"])
        lines.append(
            "\\vspace{0.4em}\\footnotesize{DOI: \\href{https://doi.org/"
            + _tex_escape(doi)
            + "}{"
            + _tex_escape(doi)
            + "}}"
        )
    lines += [
        "\\end{center}",
        "\\thispagestyle{empty}",
        "\\newpage",
        "{\\setcounter{tocdepth}{3}",
        "\\tableofcontents}",
        "\\newpage",
    ]
    return "\n".join(lines)


def _strip_latex(value: str) -> str:
    text = re.sub(r"\\[a-zA-Z@]+\*?(?:\[[^\]]*\])?(?:\{[^{}]*\})?", "", value)
    text = text.replace("{", "").replace("}", "").replace("$", "")
    text = re.sub(r"\\\\", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _extract_braced(text: str, start: int) -> tuple[str, int]:
    if start >= len(text) or text[start] != "{":
        raise ValueError("expected '{'")
    depth = 0
    index = start
    while index < len(text):
        char = text[index]
        if char == "\\":
            index += 2
            continue
        if char == "{":
            depth += 1
        elif char == "}":
            depth -= 1
            if depth == 0:
                return text[start + 1 : index], index + 1
        index += 1
    raise ValueError("unbalanced braces")


def figures_to_html(text: str, figures_dir: Path) -> str:
    def replace(match: re.Match[str]) -> str:
        body = match.group(1)
        include = INCLUDE_RE.search(body)
        if include is None:
            return match.group(0)
        filename = Path(include.group(1)).name
        if not (figures_dir / filename).is_file():
            _fail(f"HTML conversion found a missing figure: {filename}")
        caption = ""
        caption_match = CAPTION_RE.search(body)
        if caption_match:
            caption, _ = _extract_braced(body, caption_match.end() - 1)
        alt = html.escape(_strip_latex(caption), quote=True)
        return (
            '<figure class="figure">'
            f'<img src="../figures/{html.escape(filename, quote=True)}" alt="{alt}" '
            'style="max-width: 90%; height: auto;">'
            f"<figcaption>{html.escape(caption, quote=False)}</figcaption>"
            "</figure>"
        )

    return FIGURE_ENV_RE.sub(replace, text)


def _require_tool(name: str) -> str:
    executable = shutil.which(name)
    if executable is None:
        _fail(f"missing required tool {name!r} on PATH")
    return executable


def _run_step(argv: list[str], cwd: Path, log: list[str], label: str) -> None:
    completed = subprocess.run(argv, cwd=cwd, text=True, capture_output=True)
    log.append("$ " + " ".join(argv))
    log.append(completed.stdout)
    log.append(completed.stderr)
    if completed.returncode != 0:
        raise RenderError(
            f"render: {label} failed with exit {completed.returncode}; "
            f"see {cwd / '_latex_stdout.log'}"
        )


def render_pdf(
    build_dir: Path,
    combined: str,
    config: dict,
    header: str,
    figures_dir: Path,
) -> Path:
    pandoc = _require_tool("pandoc")
    xelatex = _require_tool("xelatex")
    bibtex = _require_tool("bibtex")
    build_dir.mkdir(parents=True, exist_ok=True)
    references = PROJECT_ROOT / "manuscript" / "references.bib"
    shutil.copy2(references, build_dir / "references.bib")

    markdown_path = build_dir / "_combined_manuscript.md"
    markdown_path.write_text(title_block(config) + "\n" + combined, encoding="utf-8")
    header_path = build_dir / "_preamble.tex"
    header_path.write_text(header, encoding="utf-8")

    figure_link = build_dir / "figures"
    if figure_link.is_symlink() or figure_link.exists():
        if figure_link.is_symlink():
            figure_link.unlink()
        else:
            shutil.rmtree(figure_link)
    os.symlink(figures_dir.resolve(), figure_link)

    log: list[str] = []
    try:
        _run_step(
            [
                pandoc,
                str(markdown_path),
                "-o",
                "_combined_manuscript.tex",
                "--standalone",
                "--number-sections",
                "--natbib",
                "--include-in-header",
                str(header_path),
            ],
            build_dir,
            log,
            "pandoc",
        )
        for _ in range(3):
            _run_step(
                [xelatex, "-interaction=nonstopmode", "-halt-on-error", "_combined_manuscript.tex"],
                build_dir,
                log,
                "xelatex",
            )
            if not (build_dir / "_combined_manuscript.aux").exists():
                break
            if not (build_dir / "_combined_manuscript.bbl").exists():
                _run_step([bibtex, "_combined_manuscript"], build_dir, log, "bibtex")
    finally:
        (build_dir / "_latex_stdout.log").write_text("\n".join(log), encoding="utf-8")
        if figure_link.is_symlink():
            figure_link.unlink()

    pdf_path = build_dir / "_combined_manuscript.pdf"
    if not pdf_path.is_file() or pdf_path.stat().st_size == 0:
        _fail("xelatex produced no PDF")
    if pdf_path.read_bytes()[:4] != b"%PDF":
        _fail("render output is not a PDF")
    target = build_dir / "act_inf_metaanalysis_combined.pdf"
    shutil.copy2(pdf_path, target)
    return target


def render_html(build_dir: Path, combined: str, config: dict, figures_dir: Path) -> Path:
    pandoc = _require_tool("pandoc")
    build_dir.mkdir(parents=True, exist_ok=True)
    paper = config.get("paper", {})
    authors = [str(author.get("name", "")) for author in config.get("authors", [])]
    metadata = build_dir / "_metadata.yaml"
    metadata.write_text(
        yaml.safe_dump(
            {
                "title": paper.get("title", ""),
                "subtitle": paper.get("subtitle", ""),
                "author": authors,
                "date": str(config.get("publication", {}).get("year", "")),
                "lang": str(config.get("metadata", {}).get("language", "en")),
                "keywords": [str(keyword) for keyword in config.get("keywords", [])],
            },
            sort_keys=True,
        ),
        encoding="utf-8",
    )
    markdown_path = build_dir / "_combined_manuscript.md"
    markdown_path.write_text(figures_to_html(combined, figures_dir), encoding="utf-8")
    log: list[str] = []
    _run_step(
        [
            pandoc,
            str(markdown_path),
            "-o",
            "index.html",
            "--standalone",
            "--toc",
            "--number-sections",
            "--metadata-file",
            str(metadata),
        ],
        build_dir,
        log,
        "pandoc",
    )
    (build_dir / "_pandoc_stdout.log").write_text("\n".join(log), encoding="utf-8")
    index = build_dir / "index.html"
    if not index.is_file() or index.stat().st_size == 0:
        _fail("pandoc produced no HTML")
    return index


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-root",
        type=Path,
        default=Path("output"),
        help="directory receiving pdf/ and web/ (default: output)",
    )
    parser.add_argument(
        "--manuscript-dir",
        type=Path,
        default=PROJECT_ROOT / "manuscript",
        help="manuscript source directory",
    )
    args = parser.parse_args(argv)

    output_root = args.output_root
    if not output_root.is_absolute():
        output_root = PROJECT_ROOT / output_root
    manuscript_dir = args.manuscript_dir
    figures_dir = PROJECT_ROOT / "output" / "figures"
    config = _load_yaml(manuscript_dir / "config.yaml")
    formats = config.get("render", {}).get("formats", {})
    if not formats.get("pdf") and not formats.get("html"):
        _fail("config.yaml render.formats disables both PDF and HTML")
    for disabled in ("slides", "docx", "epub"):
        if formats.get(disabled):
            _fail(f"render format {disabled!r} is enabled but has no renderer")

    variables = load_variables(PROJECT_ROOT / "output")
    sections = hydrate_sections(section_files(manuscript_dir), variables)
    combined = ("\n\n```{=latex}\n\\newpage\n```\n\n").join(text for _, text in sections)
    combined += "\n\n```{=latex}\n\\newpage\n```\n"
    registry = load_figure_registry(figures_dir)
    figures = validate_figures(combined, figures_dir, registry)
    header = preamble_tex(manuscript_dir)

    outputs: dict[str, object] = {
        "sections": len(sections),
        "figures": len(figures),
        "variables": len(variables),
        "formats": {key: bool(formats.get(key)) for key in ("pdf", "html")},
    }
    pdf_path = None
    html_path = None
    if formats.get("pdf"):
        pdf_path = render_pdf(output_root / "pdf", combined, config, header, figures_dir)
        outputs["pdf"] = str(pdf_path.relative_to(PROJECT_ROOT))
        outputs["pdf_bytes"] = pdf_path.stat().st_size
    if formats.get("html"):
        html_path = render_html(output_root / "web", combined, config, figures_dir)
        outputs["html"] = str(html_path.relative_to(PROJECT_ROOT))
        outputs["html_bytes"] = html_path.stat().st_size
    if pdf_path is None and html_path is None:
        _fail("no configured format was rendered")

    receipt = output_root / "reports" / "render_receipt.json"
    receipt.parent.mkdir(parents=True, exist_ok=True)
    receipt.write_text(json.dumps(outputs, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(outputs, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
