#!/usr/bin/env python3
"""Parse and type-check the three GNN sketches with the pinned GNN release.

The sketches are documentation, not pipeline input, so this check does not run
the repository's literature pipeline. It exercises the same GNN parser and type
checker that steps 3 and 5 use, from the exact revision in `.github/gnn-pin.json`.

The type checker follows GNN's pipeline contract: ``True`` is exit 0 (success),
``2`` is ``SUCCESS_WITH_WARNINGS`` (type/consistency problems), and ``False`` is
exit 1 (error). This gate treats warnings as findings, so only ``True`` is a
pass; ``2`` and ``False`` both exit non-zero. The printed verdict is therefore
only "verified" when the type checker actually returned ``True``.
"""

from __future__ import annotations

import json
import re
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
PIN_PATH = ROOT / ".github" / "gnn-pin.json"
SKETCH_DIR = ROOT / "gnn"
EXPECTED = 3
REQUIRED_SECTIONS = {
    "GNNSection",
    "GNNVersionAndFlags",
    "ModelName",
    "ModelAnnotation",
    "StateSpaceBlock",
    "Connections",
    "InitialParameterization",
    "Equations",
    "Time",
    "ActInfOntologyAnnotation",
    "ModelParameters",
    "Footer",
    "Signature",
}


class ConformanceError(SystemExit):
    """Raised when the pinned GNN parser rejects a sketch."""


def _read_json(path: Path) -> dict[str, Any]:
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise ConformanceError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ConformanceError(f"{path} is not valid JSON: {exc}") from exc
    if not isinstance(document, dict):
        raise ConformanceError(f"{path} must contain a JSON object")
    return document


def main() -> None:
    pin = _read_json(PIN_PATH)
    repository = pin.get("repository")
    revision = pin.get("revision")
    tag = pin.get("tag")
    if repository != "ActiveInferenceInstitute/Generalized_Notation_Notation":
        raise ConformanceError(f"unexpected GNN repository pin: {repository!r}")
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}", revision):
        raise ConformanceError("GNN pin revision must be a 40-character lowercase SHA")
    if not isinstance(tag, str) or not re.fullmatch(r"v[0-9]+\.[0-9]+\.[0-9]+", tag):
        raise ConformanceError("GNN pin tag must match vMAJOR.MINOR.PATCH")

    from gnn import __version__
    from gnn.parsers.basic import parse_gnn_formal, validate_gnn_syntax
    from gnn.type_checker import GNNTypeChecker

    expected_version = tag.removeprefix("v")
    if __version__ != expected_version:
        raise ConformanceError(f"installed GNN version {__version__!r} does not match {tag!r}")

    sketches = sorted(SKETCH_DIR.glob("h*.md"))
    if len(sketches) != EXPECTED:
        raise ConformanceError(f"expected {EXPECTED} GNN sketches, found {len(sketches)}")

    for sketch in sketches:
        content = sketch.read_text(encoding="utf-8")
        parsed = parse_gnn_formal(sketch)
        if parsed is None:
            raise ConformanceError(f"{sketch.name} did not parse")
        if getattr(parsed, "parse_errors", None):
            raise ConformanceError(f"{sketch.name} parse errors: {parsed.parse_errors!r}")
        valid, syntax_errors = validate_gnn_syntax(content)
        if not valid:
            raise ConformanceError(f"{sketch.name} syntax errors: {syntax_errors!r}")
        section_names = {section["name"] for section in parsed.sections}
        missing = sorted(REQUIRED_SECTIONS - section_names)
        if missing:
            raise ConformanceError(f"{sketch.name} is missing required sections: {missing!r}")

    with tempfile.TemporaryDirectory(prefix="metaanalysis-gnn-") as output_dir:
        type_check = GNNTypeChecker().validate_gnn_files(SKETCH_DIR, Path(output_dir))
        if type_check is not True:
            verdict = "warnings" if type_check == 2 else "error"
            raise ConformanceError(
                "GNN type checker did not accept the sketch directory: "
                f"verdict {verdict!r}, validate_gnn_files returned {type_check!r} "
                "(GNN contract: True = exit 0, 2 = warnings without --strict, "
                "False = exit 1)"
            )

    print(
        json.dumps(
            {
                "gnn-version": __version__,
                "pin-revision": revision,
                "sketches": len(sketches),
                "parsed": len(sketches),
                "type-checked": len(sketches),
                "type-checker-result": type_check,
                "result": "verified",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
