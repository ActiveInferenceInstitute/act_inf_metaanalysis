"""Real subprocess imports exercise template-root admission and standalone use."""

from __future__ import annotations

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

PROJECT = Path(__file__).resolve().parents[1]


def _template(path: Path) -> Path:
    package = path / "infrastructure"
    package.mkdir(parents=True)
    (package / "__init__.py").write_text("", encoding="utf-8")
    return package / "__init__.py"


def _run(cwd: Path, root: str | None, *, infrastructure: bool = True):
    project = cwd / "standalone-fixture"
    scripts = project / "scripts"
    scripts.mkdir(parents=True)
    shutil.copy2(PROJECT / "scripts" / "_bootstrap.py", scripts / "_bootstrap.py")
    (project / "src").symlink_to(PROJECT / "src", target_is_directory=True)
    environment = dict(os.environ)
    environment.pop("TEMPLATE_REPO_ROOT", None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    if root is not None:
        environment["TEMPLATE_REPO_ROOT"] = root
    code = (
        "import sys; from pathlib import Path; "
        f"sys.path.insert(0, {str(scripts)!r}); "
        "from _bootstrap import bootstrap_project; "
        f"bootstrap_project(include_infrastructure={infrastructure!r}); "
        + ("import infrastructure; print(Path(infrastructure.__file__).resolve())"
           if infrastructure else "import config; print(Path(config.__file__).resolve())")
    )
    return subprocess.run(
        [sys.executable, "-c", code], cwd=cwd, env=environment,
        text=True, capture_output=True, timeout=20,
    )


@pytest.mark.parametrize("invalid", ["", "missing"])
def test_explicit_invalid_root_never_falls_through(tmp_path: Path, invalid: str):
    _template(tmp_path / "template")
    configured = "" if invalid == "" else str(tmp_path / "missing")
    result = _run(tmp_path, configured)
    assert result.returncode != 0
    assert "TEMPLATE_REPO_ROOT" in result.stderr
    assert not result.stdout.strip()


def test_explicit_root_wins_over_cwd_template(tmp_path: Path):
    _template(tmp_path / "cwd" / "template")
    expected = _template(tmp_path / "selected")
    result = _run(tmp_path / "cwd", str(tmp_path / "selected"))
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()) == expected.resolve()


def test_unset_root_retains_documented_ancestor_discovery(tmp_path: Path):
    expected = _template(tmp_path / "template")
    cwd = tmp_path / "nested" / "work"
    cwd.mkdir(parents=True)
    result = _run(cwd, None)
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()) == expected.resolve()


def test_standalone_bootstrap_does_not_require_template(tmp_path: Path):
    result = _run(tmp_path, str(tmp_path / "missing"), infrastructure=False)
    assert result.returncode == 0, result.stderr
    assert Path(result.stdout.strip()) == PROJECT / "src" / "config.py"
