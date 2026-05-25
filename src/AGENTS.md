# Source Code — Agent Directives

**Archived module root** at `projects_archive/act_inf_metaanalysis/src/`.

## Core Rules (Apply to All Subpackages)

1. **Thin orchestrator pattern**: No analysis logic in `scripts/`. All computation lives in `src/`.
   Scripts import from `src/` and handle only file I/O, argument parsing, and logging.

2. **No mock policy**: All tests use real data, real files, real computations (615 tests across 39 files as of 2026-05-25).
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

## Pipeline runner modules (orchestration in `src/`)

| Module | Script | Role |
| --- | --- | --- |
| `literature/search_runner.py` | `01_literature_search.py` | Multi-source retrieval, relevance filter, corpus save |
| `analysis/pipeline_runner.py` | `02_meta_analysis_pipeline.py` | Bibliometrics, TF-IDF, topics, citation network |
| `knowledge_graph/kg_runner.py` | `03_build_knowledge_graph.py` | LLM extraction, hypothesis scoring, assertion summary |
| `visualization/figure_runner.py` | `04_generate_figures.py` | 16 figures from JSON artifacts |
| `literature/fulltext_assessment.py` | `06_fulltext_assessment.py` | OA / PDF availability report |
| `config_loader.py` | scripts 01, 03 | YAML `project_config` loading |

Shared script utilities: `scripts/_bootstrap.py` (path setup), `scripts/_io.py` (JSON helpers).

## Current Test Count

615 tests across 39 files. Run: `uv run pytest tests/ -q --cov=src --cov-fail-under=90`

See each subpackage's `AGENTS.md` for module-specific constraints.
