"""Shared sys.path bootstrap for project orchestrator scripts."""

from __future__ import annotations

import logging
import sys
import os
from pathlib import Path

logger = logging.getLogger(__name__)


def bootstrap_project(*, include_infrastructure: bool = False) -> Path:
    """Insert ``src/`` (and optionally template repo root) on ``sys.path``.

    Returns:
        Project root directory (parent of ``scripts/``).
    """
    root = Path(__file__).resolve().parent.parent
    src = root / "src"
    src_text = str(src)
    if src_text not in sys.path:
        sys.path.insert(0, src_text)
    if include_infrastructure:
        # Resolve the template root deterministically: TEMPLATE_REPO_ROOT first
        # (if set), then the project-local `template/` directory. Scanning the
        # process CWD and arbitrary ancestor directories for any `infrastructure/`
        # dir is non-deterministic and can import an unrelated tree, so it is
        # only used as a last resort and always logged (MED-11).
        selected: Path | None = None
        configured_root = os.environ.get("TEMPLATE_REPO_ROOT")
        if configured_root:
            candidate = Path(configured_root)
            if (candidate / "infrastructure").is_dir():
                selected = candidate
        if selected is None and (root / "template" / "infrastructure").is_dir():
            selected = root / "template"
        if selected is None:
            for candidate in [Path.cwd(), *Path.cwd().parents, *root.parents]:
                for probe in (candidate, candidate / "template"):
                    if (probe / "infrastructure").is_dir():
                        selected = probe
                        logger.warning(
                            "template infrastructure root resolved from %s — "
                            "set TEMPLATE_REPO_ROOT to pin it explicitly",
                            probe,
                        )
                        break
                if selected is not None:
                    break
        if selected is not None:
            template_text = str(selected)
            if template_text not in sys.path:
                sys.path.insert(0, template_text)
            logger.debug("Using template infrastructure root: %s", selected)
    return root
