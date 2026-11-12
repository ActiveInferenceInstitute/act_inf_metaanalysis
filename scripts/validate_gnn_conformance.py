#!/usr/bin/env python3
"""Parse and type-check the three GNN sketches with the pinned GNN release.

The sketches are documentation, not pipeline input, so this check does not run
the repository's literature pipeline. It exercises the same GNN parser and type
checker that steps 3 and 5 use, from the exact revision in `.github/gnn-pin.json`.

``GNNTypeChecker.validate_gnn_files`` returns ``True`` when every file validates,
``2`` when files are invalid or none were found (the warnings/"completed with
issues" outcome) and ``False`` on a hard failure. Only ``True`` passes here; the
receipt records the raw value as ``type-checker-result``. ``validate_gnn_syntax`` is
called with ``is_content=True`` so the sketch text is not probed as a path.
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
        valid, syntax_errors = validate_gnn_syntax(content, is_content=True)
        if not valid:
            raise ConformanceError(f"{sketch.name} syntax errors: {syntax_errors!r}")
        section_names = {section["name"] for section in parsed.sections}
        missing = sorted(REQUIRED_SECTIONS - section_names)
        if missing:
            raise ConformanceError(f"{sketch.name} is missing required sections: {missing!r}")

    with tempfile.TemporaryDirectory(prefix="metaanalysis-gnn-") as output_dir:
        type_check_result = GNNTypeChecker().validate_gnn_files(SKETCH_DIR, Path(output_dir))
        if type_check_result is not True:
            kind = "warnings" if type_check_result == 2 else "error"
            raise ConformanceError(
                f"GNN type checker reported {kind} for the sketch directory "
                f"(returned {type_check_result!r}); only True passes"
            )

    print(
        json.dumps(
            {
                "gnn-version": __version__,
                "pin-revision": revision,
                "sketches": len(sketches),
                "parsed": len(sketches),
                "type-checked": len(sketches),
                "type-checker-result": type_check_result,
                "result": "verified",
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
