#!/usr/bin/env python3
"""Check relative documentation links and the documentation index.

This repository has no mkdocs or markdown-link-check configuration, so this
script is the documentation check the `docs` gate arm runs. It verifies:

1. every relative link in tracked Markdown resolves to a file in the tree;
2. fragment links to Markdown headings resolve to a heading slug;
3. ``docs/documentation-index.md`` exists and lists every long-lived guide in
   ``doc/``; ``docs/README.md`` is the hub.

External URLs and ``mailto:`` targets are not fetched: the check is offline by
design, so it never turns a network failure into a documentation verdict.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED_DIRS = {
    ".git",
    ".venv",
    ".gnn-env",
    ".render-check",
    ".gate-logs",
    ".ruff_cache",
    ".pytest_cache",
    "__pycache__",
    "output",
}
LINK_RE = re.compile(r"(?<!!)\[[^\]]*\]\(([^)\s]+)(?:\s+\"[^\"]*\")?\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*?)\s*#*\s*$")
SCHEMES = ("http://", "https://", "mailto:", "tel:", "data:", "ftp:")


def markdown_files(root: Path) -> list[Path]:
    files = []
    for path in sorted(root.rglob("*.md")):
        relative = path.relative_to(root)
        if any(part in EXCLUDED_DIRS for part in relative.parts):
            continue
        files.append(path)
    return files


def github_slug(heading: str) -> str:
    text = heading.strip().lower()
    text = re.sub(r"`([^`]*)`", r"\1", text)
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)
    text = re.sub(r"[^\w\s-]", "", text, flags=re.UNICODE)
    return re.sub(r"\s+", "-", text).strip("-")


def heading_slugs(path: Path) -> set[str]:
    slugs: set[str] = set()
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        match = HEADING_RE.match(line)
        if match:
            slugs.add(github_slug(match.group(1)))
    return slugs


def check_links(files: list[Path]) -> tuple[list[str], int]:
    errors: list[str] = []
    checked = 0
    slug_cache: dict[Path, set[str]] = {}
    for source in files:
        text = source.read_text(encoding="utf-8", errors="replace")
        for match in LINK_RE.finditer(text):
            target = match.group(1).strip("<>")
            if not target or target.startswith(SCHEMES) or target.startswith("#"):
                continue
            checked += 1
            path_part, _, fragment = target.partition("#")
            path_part = path_part.split("?", 1)[0]
            destination = (source.parent / path_part).resolve()
            if not destination.exists():
                errors.append(
                    f"{source.relative_to(ROOT)}: missing link target {target!r}"
                )
                continue
            if fragment and destination.suffix == ".md":
                if destination not in slug_cache:
                    slug_cache[destination] = heading_slugs(destination)
                if fragment.lower() not in slug_cache[destination]:
                    errors.append(
                        f"{source.relative_to(ROOT)}: missing anchor {fragment!r} "
                        f"in {destination.relative_to(ROOT)}"
                    )
    return errors, checked


def check_index(root: Path) -> list[str]:
    errors = []
    hub = root / "docs" / "README.md"
    if not hub.exists():
        errors.append("docs/README.md is missing")
    index = root / "docs" / "documentation-index.md"
    if not index.exists():
        return errors + ["docs/documentation-index.md is missing"]
    text = index.read_text(encoding="utf-8")
    for path in sorted((root / "doc").glob("*.md")):
        if path.name in {"AGENTS.md", "README.md"}:
            continue
        if path.name not in text:
            errors.append(f"docs/documentation-index.md does not list doc/{path.name}")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root",
        type=Path,
        default=ROOT,
        help="repository root to check (default: this checkout)",
    )
    args = parser.parse_args(argv)
    root = args.root.resolve()
    checker = root / "scripts" / "gate" / "identity.py"
    for artifact in (
        "docs/workflows/record-identity.schema.json",
        "scripts/gate/identity.py",
        ".github/gnn-pin.json",
    ):
        result = subprocess.run(
            [sys.executable, str(checker), "--verify-copy", artifact],
            cwd=root,
            stdin=subprocess.DEVNULL,
            check=False,
        )
        if result.returncode:
            return result.returncode
    files = markdown_files(root)
    errors, checked = check_links(files)
    errors.extend(check_index(root))
    if errors:
        for error in errors:
            print(f"docs: {error}", file=sys.stderr)
        print(f"docs: {len(errors)} problem(s) in {len(files)} markdown files", file=sys.stderr)
        return 1
    print(f"docs: checked {len(files)} markdown files and {checked} relative links")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
