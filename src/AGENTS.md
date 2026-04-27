# Source Code — Agent Directives

**Active module root** at `projects/act_inf_metaanalysis/src/`.

## Core Rules (Apply to All Subpackages)

1. **Thin orchestrator pattern**: No analysis logic in `scripts/`. All computation lives in `src/`.
   Scripts import from `src/` and handle only file I/O, argument parsing, and logging.

2. **No mock policy**: All 553 tests use real data, real files, real computations.
   - HTTP: use `pytest-httpserver`
   - Files: use `tmp_path` fixture
   - Never `unittest.mock.patch`, `MagicMock`, or `monkeypatch` for mocking logic

3. **Determinism**: All stochastic operations use `seed=42`. Never remove seeds.

4. **PYTHONPATH requirement**: When running scripts manually, set:
   ```
   PYTHONPATH=/path/to/template:/path/to/act_inf_metaanalysis/src
   ```
   The first entry enables infrastructure imports; the second enables `from literature.models import Paper`.

5. **Coverage gates**: `tests/` targets 90%+ coverage. A pipeline run fails if coverage drops below this.

## Dependency Graph (No Circular Imports)

```
manuscript ──────────────────────────────────── (reads output JSONs only)
visualization ──────────────────────────────── (reads analysis data, no src imports)
knowledge_graph ──→ literature.models
analysis ──────────→ literature.models
literature ─────────────────────────────────── (no src/ dependencies)
```

Do not introduce imports that create cycles in this graph.

## Adding a New Module

1. Place in the appropriate subpackage directory.
2. Export from the subpackage's `__init__.py` if needed by other modules.
3. Write tests in `tests/<subpackage>/test_<module>.py`.
4. Import in the relevant `scripts/` file as the only orchestration point.
5. Update the subpackage `README.md` and `AGENTS.md`.

## Current Test Count

553 tests, 9 warnings (all `rdflib` deprecation notices unrelated to project code).
Run: `PYTHONPATH=... .venv/bin/python -m pytest tests/ -q`

See each subpackage's `AGENTS.md` for module-specific constraints.
