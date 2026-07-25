"""Shared sys.path bootstrap for project orchestrator scripts."""

from __future__ import annotations

import sys
import os
from pathlib import Path


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
        candidates: list[Path] = []
        configured_root = os.environ.get("TEMPLATE_REPO_ROOT")
        if configured_root:
            candidates.append(Path(configured_root))
        candidates.extend([Path.cwd(), *Path.cwd().parents, root, *root.parents])
        candidates.extend(parent / "template" for parent in [root, *root.parents])
        template_root = next(
            (
                candidate
                for candidate in candidates
                if (candidate / "infrastructure").is_dir()
            ),
            None,
        )
        if template_root is not None:
            template_text = str(template_root)
            if template_text not in sys.path:
                sys.path.insert(0, template_text)
    return root
