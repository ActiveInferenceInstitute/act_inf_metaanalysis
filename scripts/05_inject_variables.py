#!/usr/bin/env python3
"""Template-compatible wrapper for the canonical manuscript hydrator."""

from __future__ import annotations

import sys
from pathlib import Path

_SCRIPTS = Path(__file__).resolve().parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from z_generate_manuscript_variables import main


if __name__ == "__main__":
    raise SystemExit(main())
