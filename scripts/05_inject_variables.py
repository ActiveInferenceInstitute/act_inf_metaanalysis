#!/usr/bin/env python3
"""Manuscript variable injection script.

Reads pipeline output data, computes template variables, and injects
them into manuscript markdown files. Produces rendered copies in
output/manuscript/ with all {{VAR}} placeholders replaced by real values.

Usage:
    python scripts/05_inject_variables.py [--project PROJECT]
"""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root.parent.parent))

from infrastructure.core.logging_utils import get_logger, log_operation
from src.manuscript.variables import compute_variables, inject_variables

logger = get_logger(__name__)


def main() -> int:
    """Execute manuscript variable injection."""
    parser = argparse.ArgumentParser(
        description="Inject pipeline variables into manuscript templates"
    )
    parser.add_argument(
        "--project",
        default="act_inf_metaanalysis",
        help="Project name (default: act_inf_metaanalysis)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files",
    )
    args = parser.parse_args()

    # Resolve paths
    repo_root = Path(__file__).resolve().parent.parent.parent.parent
    project_dir = repo_root / "projects" / args.project
    manuscript_dir = project_dir / "manuscript"
    output_dir = project_dir / "output"
    rendered_dir = output_dir / "manuscript"

    if not manuscript_dir.exists():
        logger.error("Manuscript directory not found: %s", manuscript_dir)
        return 1

    if not output_dir.exists():
        logger.error("Output directory not found: %s", output_dir)
        return 1

    with log_operation("Manuscript variable injection"):
        # Step 1: Compute variables from pipeline output
        logger.info("Computing variables from pipeline output: %s", output_dir)
        variables = compute_variables(output_dir)
        logger.info("Computed %d template variables", len(variables))

        # Log variable values for audit trail
        for key in sorted(variables.keys()):
            logger.debug("  %s = %s", key, variables[key])

        # Step 2: Create output directory
        rendered_dir.mkdir(parents=True, exist_ok=True)

        # Step 3: Process each manuscript file
        md_files = sorted(manuscript_dir.glob("*.md"))
        total_injected = 0
        files_changed = 0

        for md_file in md_files:
            content = md_file.read_text(encoding="utf-8")

            # Inject variables
            rendered = inject_variables(content, variables, filename=md_file.name)

            if rendered != content:
                files_changed += 1
                # Count replacements
                import re

                original_vars = re.findall(r"\{\{(\w+)\}\}", content)
                remaining_vars = re.findall(r"\{\{(\w+)\}\}", rendered)
                injected = len(original_vars) - len(remaining_vars)
                total_injected += injected

            if args.dry_run:
                if rendered != content:
                    logger.info(
                        "  [DRY RUN] Would update %s (%d variables)",
                        md_file.name,
                        len(re.findall(r"\{\{(\w+)\}\}", content))
                        - len(re.findall(r"\{\{(\w+)\}\}", rendered)),
                    )
            else:
                # Write rendered copy
                out_path = rendered_dir / md_file.name
                out_path.write_text(rendered, encoding="utf-8")

        # Step 4: Copy non-md files (config.yaml, references.bib, etc.)
        for other_file in manuscript_dir.iterdir():
            if other_file.suffix != ".md" and other_file.is_file():
                dest = rendered_dir / other_file.name
                if not args.dry_run:
                    shutil.copy2(other_file, dest)
                logger.debug("Copied %s to output/manuscript/", other_file.name)

        # Step 5: Verify no unresolved variables in critical files
        if not args.dry_run:
            import re

            unresolved = {}
            for out_file in sorted(rendered_dir.glob("*.md")):
                content = out_file.read_text(encoding="utf-8")
                remaining = re.findall(r"\{\{(\w+)\}\}", content)
                if remaining:
                    unresolved[out_file.name] = remaining

            if unresolved:
                logger.warning("Unresolved template variables found:")
                for fname, vars_list in unresolved.items():
                    logger.warning(
                        "  %s: %s", fname, ", ".join(sorted(set(vars_list)))
                    )
            else:
                logger.info("All template variables resolved successfully")

        # Summary
        logger.info(
            "Variable injection complete: %d variables injected across %d files",
            total_injected,
            files_changed,
        )
        logger.info("Rendered manuscript files written to: %s", rendered_dir)

    return 0


if __name__ == "__main__":
    sys.exit(main())
