#!/bin/sh
# Single entry point for every local gate arm.
#
#   ./run.sh              # default quick arm: fast tests
#   ./run.sh lint         # ruff, the same command the CI workflow runs
#   ./run.sh types        # mypy over src/
#   ./run.sh test-fast    # pytest without the slow figure tests, no coverage gate
#   ./run.sh test-full    # pytest with the 90% coverage gate
#   ./run.sh docs         # relative-link and documentation-index check
#   ./run.sh gnn          # pinned GNN conformance parse/type check
#   ./run.sh render       # manuscript PDF/HTML render into .render-check/
#   ./run.sh all          # lint, types, test-full, docs, gnn, render
#   ./run.sh bench        # time every arm and refresh doc/_generated/gate_arms.md
#   ./run.sh --list
#
# The arm commands live in scripts/gate.py so the workflow, the docs and this
# script cannot drift apart.
set -eu
ROOT=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
exec uv run --project "$ROOT" python "$ROOT/scripts/gate.py" "$@"
