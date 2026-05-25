# Thermo-Nuclear Code Quality Audit — `act_inf_metaanalysis`

**Date:** 2026-05-24  
**Scope:** `projects_archive/act_inf_metaanalysis/` (archived; not template pipeline–discovered)  
**Rubric:** template thermo-nuclear maintainability review (1k-line rule, script gates, thin orchestrators, zero-mock tests)

## Executive verdict

**Conditional pass → remediated (W1/W2 complete).** The archive had no presumptive 1k-line blockers and a clean package DAG, but four orchestration scripts exceeded the 250-line fail gate, analysis logic leaked into script 02, LLM extraction tests were thin, and root docs claimed active `projects/` status. Remediation waves W1 and W2 are implemented; verification gates pass.

---

## Metrics snapshot (post-remediation)

| Metric | Before | After |
|--------|--------|-------|
| Tests collected | 557 (1 failure on script import) | **568 passed** |
| `src/` coverage | ~84% (mid-refactor) | **91.64%** (≥90% gate) |
| Test files | 25 | **30** |
| Scripts >250 lines | **4** (326–359 lines) | **0** (max 91 lines) |
| Largest `src/` module | 556 (`llm_extraction.py`) | 500 (`subfield_classifier.py`) |
| Module line-count gate (repo root) | N/A (archive paths) | **PASS** |

### Script line counts (after W1)

| Lines | File |
|------:|------|
| 25 | `scripts/_bootstrap.py`, `scripts/_io.py` |
| 52 | `scripts/04_generate_figures.py` |
| 59 | `scripts/02_meta_analysis_pipeline.py` |
| 62 | `scripts/03_build_knowledge_graph.py` |
| 63 | `scripts/01_literature_search.py` |
| 65 | `scripts/06_fulltext_assessment.py` |
| 91 | `scripts/05_inject_variables.py` |

### Largest `src/` modules (after W2 splits)

| Lines | File |
|------:|------|
| 500 | `src/analysis/subfield_classifier.py` |
| 430 | `src/manuscript/variables.py` |
| 389 | `src/knowledge_graph/nanopublication.py` |
| 225 | `src/knowledge_graph/llm_extraction.py` (orchestrator; was 556) |
| 204 | `src/visualization/advanced/embeddings.py` |

---

## Findings by wave

### W1 — Must-fix (completed)

1. **Script bloat / repeated bootstrap** — Added `scripts/_bootstrap.py` and `scripts/_io.py`; moved pipeline bodies to `src/literature/search_runner.py`, `src/analysis/pipeline_runner.py`, `src/knowledge_graph/kg_runner.py`, `src/visualization/figure_runner.py`, `src/literature/fulltext_assessment.py`.
2. **Thin-orchestrator violations in script 02** — Subfield timeline → `src/analysis/temporal_analysis.py` (`compute_subfield_timeline`); document tokenization → `src/analysis/text_processing.py` (`tokenize_documents`).
3. **Thin LLM extraction tests** — Expanded `tests/knowledge_graph/test_extraction.py` with `pytest-httpserver` Ollama stub (real HTTP, no mocks).
4. **Documentation drift** — Root `AGENTS.md`, `README.md`, `doc/*`, and `scripts/README.md` now state **archived** status and `projects_archive/` paths; test counts refreshed to **568 / 30 files**.

### W2 — Should-fix (completed)

1. **`advanced_plots.py` split** — `src/visualization/advanced/` (`labels`, `word_cloud`, `embeddings`, `topics`) + re-export shim in `advanced_plots.py`.
2. **`llm_extraction.py` split** — `llm_config.py`, `llm_client.py`, `llm_prompts.py`; slim orchestrator in `llm_extraction.py` with backward-compat aliases.
3. **Config-driven search queries** — `DEFAULT_ARXIV_QUERIES` / `DEFAULT_RELEVANCE_KEYWORDS` in `src/config.py`; `src/config_loader.py` loads `project_config.search` from `manuscript/config.yaml` with defaults.
4. **Example config** — Added `manuscript/config.yaml.example` (stripped template).

### W3 — Deferred

1. Split `tests/knowledge_graph/test_llm_extraction.py` (758 lines) — fixture-heavy; lower ROI.
2. Nested `.git/` in project root — document only; remove after confirming no standalone clone dependency.
3. Refactor `subfield_classifier.py` (500 lines) — only if keyword lists grow further.
4. Raise coverage on `figure_runner.py` and `search_runner.py` — optional; gate already met.

---

## Code-judo decomposition (before → after)

| Area | Before | After | Target |
|------|--------|-------|--------|
| Script 01 | 359 lines | 63 | ≤250 ✓ |
| Script 02 | 326 | 59 | ≤250 ✓ |
| Script 03 | 351 | 62 | ≤250 ✓ |
| Script 04 | 347 | 52 | ≤250 ✓ |
| `llm_extraction.py` | 556 | 225 + helpers | ≤250 per module ✓ |
| `advanced_plots.py` | 528 | 20 shim + subpackage | ≤204 per module ✓ |

---

## Verification checklist

Run from project root:

```bash
cd projects_archive/act_inf_metaanalysis
uv sync --extra dev
uv run pytest tests/ -q --cov=src --cov-fail-under=90
find scripts -name '*.py' | xargs wc -l   # all orchestrators ≤250
```

From template repository root:

```bash
uv run python scripts/gates/module_line_count_check.py
```

**Approval bar (W1+W2):**

- [x] All `scripts/*.py` ≤250 lines
- [x] No analysis logic in scripts (timeline/tokenization in `src/analysis/`)
- [x] `test_extraction.py` exercises httpserver LLM path
- [x] Docs reference `projects_archive/` and archived-not-discovered status
- [x] Coverage ≥90%, zero failures/skips (568 passed)

---

## Non-code notes

- **Archive location:** Not executed by `./run.sh` until promoted to `projects/`.
- **Optional infrastructure coupling:** Script 04 / `figure_runner` lazy-imports template `infrastructure` when present; standalone archive runs without it.
- **Pre-populated `output/`:** Expected for snapshot; do not commit on re-promotion.
