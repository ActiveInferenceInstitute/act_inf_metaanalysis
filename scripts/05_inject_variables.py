#!/usr/bin/env python3
"""Manuscript variable injection script (thin wrapper)."""

from __future__ import annotations

import argparse
import logging
import re
import shutil
import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from _bootstrap import bootstrap_project

PROJECT_ROOT = bootstrap_project()

from manuscript.variables import compute_variables, inject_variables, write_zenodo_metadata

logger = logging.getLogger(__name__)


def resolve_project_dir(project_name: str) -> Path:
    """Locate project under projects/, archive/, or in_progress/."""
    repo_root = PROJECT_ROOT.parent.parent
    for base in ("projects", "projects_archive", "projects_in_progress"):
        candidate = repo_root / base / project_name
        if candidate.exists():
            return candidate
    return repo_root / "projects" / project_name


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Inject pipeline variables into manuscript templates"
    )
    parser.add_argument("--project", default="act_inf_metaanalysis")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)
    project_dir = PROJECT_ROOT
    manuscript_dir = project_dir / "manuscript"
    output_dir = project_dir / "output"
    rendered_dir = output_dir / "manuscript"

    if not manuscript_dir.exists():
        logger.error("Manuscript directory not found: %s", manuscript_dir)
        return 1
    if not output_dir.exists():
        logger.error("Output directory not found: %s", output_dir)
        return 1

    variables = compute_variables(output_dir, project_root=project_dir)
    rendered_dir.mkdir(parents=True, exist_ok=True)
    zenodo_path = output_dir / "reports" / "zenodo_deposit_metadata.json"
    if not args.dry_run:
        write_zenodo_metadata(variables, zenodo_path)
        logger.info("Wrote Zenodo metadata: %s", zenodo_path)
    files_changed = 0
    total_injected = 0

    for md_file in sorted(manuscript_dir.glob("*.md")):
        content = md_file.read_text(encoding="utf-8")
        lenient = md_file.name in ("02e_methods_viz_injection.md", "AGENTS.md")
        rendered = inject_variables(
            content, variables, filename=md_file.name, lenient=lenient
        )
        if rendered != content:
            files_changed += 1
            total_injected += len(re.findall(r"\{\{(\w+)\}\}", content)) - len(
                re.findall(r"\{\{(\w+)\}\}", rendered)
            )
        if not args.dry_run:
            (rendered_dir / md_file.name).write_text(rendered, encoding="utf-8")

    if not args.dry_run:
        for other_file in manuscript_dir.iterdir():
            if other_file.suffix != ".md" and other_file.is_file():
                shutil.copy2(other_file, rendered_dir / other_file.name)

    logger.info(
        "Variable injection complete: %d variables injected across %d files",
        total_injected,
        files_changed,
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
