"""Shared sys.path bootstrap for project orchestrator scripts."""

from __future__ import annotations

import sys
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
        repo_root = root.parent.parent
        repo_text = str(repo_root)
        if repo_text not in sys.path:
            sys.path.insert(0, repo_text)
    return root
