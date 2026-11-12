"""The GNN conformance script must fail closed on the type-checker sentinel.

``GNNTypeChecker.validate_gnn_files`` returns ``True`` (all valid), ``2`` (invalid
files or none found) or ``False`` (hard failure). The pinned parser is installed only
in the gate environment, so these tests substitute small hand-written stand-in
modules for ``gnn`` and exercise the script's real ``main()`` over the real sketches.
"""

from __future__ import annotations

import importlib.util
import json
import sys
import types
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "validate_gnn_conformance.py"


def _load_script():
    spec = importlib.util.spec_from_file_location("validate_gnn_conformance_under_test", SCRIPT)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _install_stand_in(monkeypatch: pytest.MonkeyPatch, module, outcome: object) -> list[dict]:
    pin = json.loads(module.PIN_PATH.read_text(encoding="utf-8"))
    syntax_calls: list[dict] = []

    class Checker:
        def validate_gnn_files(self, directory, output_dir):
            return outcome

    def parse_gnn_formal(path):
        text = Path(path).read_text(encoding="utf-8")
        names = [
            line.strip().removeprefix("## ") for line in text.splitlines() if line.startswith("## ")
        ]
        return types.SimpleNamespace(parse_errors=[], sections=[{"name": name} for name in names])

    def validate_gnn_syntax(content, **kwargs):
        syntax_calls.append(kwargs)
        return True, []

    gnn = types.ModuleType("gnn")
    gnn.__version__ = pin["tag"].removeprefix("v")
    parsers = types.ModuleType("gnn.parsers")
    basic = types.ModuleType("gnn.parsers.basic")
    basic.parse_gnn_formal = parse_gnn_formal
    basic.validate_gnn_syntax = validate_gnn_syntax
    checker = types.ModuleType("gnn.type_checker")
    checker.GNNTypeChecker = Checker
    for name, mod in {
        "gnn": gnn,
        "gnn.parsers": parsers,
        "gnn.parsers.basic": basic,
        "gnn.type_checker": checker,
    }.items():
        monkeypatch.setitem(sys.modules, name, mod)
    return syntax_calls


@pytest.mark.parametrize(("outcome", "kind"), [(2, "warnings"), (False, "error"), (None, "error")])
def test_non_true_type_checker_outcome_fails(monkeypatch, outcome, kind):
    module = _load_script()
    _install_stand_in(monkeypatch, module, outcome)
    with pytest.raises(module.ConformanceError) as excinfo:
        module.main()
    assert kind in str(excinfo.value)
    assert f"returned {outcome!r}" in str(excinfo.value)


def test_true_outcome_passes_and_receipt_records_it(monkeypatch, capsys):
    module = _load_script()
    calls = _install_stand_in(monkeypatch, module, True)
    module.main()
    receipt = json.loads(capsys.readouterr().out)
    assert receipt["type-checker-result"] is True
    assert receipt["result"] == "verified"
    assert calls and all(call == {"is_content": True} for call in calls)
