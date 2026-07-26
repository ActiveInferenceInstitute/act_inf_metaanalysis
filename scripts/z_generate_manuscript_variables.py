#!/usr/bin/env python3
"""Template-recognized manuscript hydration entrypoint."""

from __future__ import annotations

import argparse
import logging
import shutil
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

from manuscript.variables import (
    TOKEN_RE,
    collect_manuscript_tokens,
    compute_variables,
    inject_variables,
    write_manuscript_variables,
    write_zenodo_metadata,
)

logger = logging.getLogger(__name__)
_EXCLUDED = {"AGENTS.md", "README.md", "SKILL.md", "SYNTAX.md"}


def resolve_project_dir(project: str) -> Path:
    candidate = Path(project).expanduser()
    if candidate.exists():
        return candidate.resolve()
    return PROJECT_ROOT


def hydrate(project_dir: Path, *, dry_run: bool = False) -> tuple[int, int]:
    manuscript_dir = project_dir / "manuscript"
    output_dir = project_dir / "output"
    rendered_dir = output_dir / "manuscript"
    if not manuscript_dir.exists():
        raise FileNotFoundError(f"Manuscript directory not found: {manuscript_dir}")
    if not output_dir.exists():
        raise FileNotFoundError(f"Output directory not found: {output_dir}")

    variables = compute_variables(output_dir, project_root=project_dir)
    token_map = collect_manuscript_tokens(manuscript_dir)
    missing = sorted(set(token_map) - set(variables))
    if missing:
        raise RuntimeError("Missing manuscript variables: " + ", ".join(missing))

    rendered_files = 0
    injected = 0
    rendered_contents: dict[str, str] = {}
    for source in sorted(manuscript_dir.glob("*.md")):
        if source.name in _EXCLUDED:
            continue
        content = source.read_text(encoding="utf-8")
        rendered = inject_variables(content, variables, filename=source.name)
        rendered_contents[source.name] = rendered
        rendered_files += 1
        injected += len(TOKEN_RE.findall(content))

    if dry_run:
        logger.info("Dry-run hydration passed for %d manuscript files", rendered_files)
        return rendered_files, injected

    rendered_dir.mkdir(parents=True, exist_ok=True)
    for existing in rendered_dir.iterdir():
        if existing.is_dir() and not existing.is_symlink():
            shutil.rmtree(existing)
        else:
            existing.unlink()
    for name, content in rendered_contents.items():
        (rendered_dir / name).write_text(content, encoding="utf-8")
    for other in manuscript_dir.iterdir():
        if other.is_file() and other.suffix != ".md":
            shutil.copy2(other, rendered_dir / other.name)

    variables_path = write_manuscript_variables(output_dir, project_dir, variables)
    write_zenodo_metadata(
        variables,
        output_dir / "reports" / "zenodo_deposit_metadata.json",
    )
    logger.info("Wrote manuscript variables: %s", variables_path)
    logger.info(
        "Hydrated %d manuscript files with %d source token occurrences",
        rendered_files,
        injected,
    )
    return rendered_files, injected


def main() -> int:
    parser = argparse.ArgumentParser(description="Hydrate manuscript variables")
    parser.add_argument("--project", default=str(PROJECT_ROOT))
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO)
    hydrate(resolve_project_dir(args.project), dry_run=args.dry_run)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
