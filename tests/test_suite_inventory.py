"""Test-suite inventory guards.

Regression guards against silent test loss (MED-09) and other suite-integrity
issues: duplicate top-level class definitions in a module silently shadow the
first definition during pytest collection, so no test from the shadowed class
ever runs. This module AST-scans the whole test tree to detect that class of
bug without depending on a volatile total-test count.
"""

from __future__ import annotations

import ast
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent
_TEST_DIR = _REPO_ROOT


def _iter_test_modules():
    for path in sorted(_TEST_DIR.rglob("test_*.py")):
        yield path.read_text(encoding="utf-8"), str(path.relative_to(_REPO_ROOT))


def test_no_duplicate_top_level_class_definitions():
    """No test module defines the same top-level class name twice.

    pytest collects classes by walking module attributes *after* the whole
    module is imported, so a redefinition replaces the earlier class and its
    tests are silently never collected. (Historically `TestCorpusFilterBySubfield`
    was defined twice in `test_corpus.py`, dropping four tests.)
    """
    offenders: list[str] = []
    for source, name in _iter_test_modules():
        tree = ast.parse(source)
        seen: dict[str, int] = {}
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name not in seen:
                seen[node.name] = node.lineno
            elif isinstance(node, ast.ClassDef):
                offenders.append(f"{name}:{node.lineno} redefines {node.name}")
    assert not offenders, "Duplicate top-level class definitions found:\n" + "\n".join(offenders)


def test_every_test_class_defines_collectable_tests():
    """Every top-level class with a `test_*` prefix must define at least one
    `test_*` method (a class with none is dead weight and hints at an intent
    error)."""
    for source, name in _iter_test_modules():
        tree = ast.parse(source)
        for node in tree.body:
            if not isinstance(node, ast.ClassDef) or not node.name.startswith("Test"):
                continue
            n_methods = sum(
                1
                for child in node.body
                if isinstance(child, (ast.FunctionDef, ast.AsyncFunctionDef))
                and child.name.startswith("test")
            )
            assert n_methods > 0, (
                f"{name}:{node.lineno} class {node.name} defines no test methods"
            )
