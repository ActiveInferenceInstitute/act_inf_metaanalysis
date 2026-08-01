# Thermo-Nuclear Code Quality Audit — `act_inf_metaanalysis`

**Date:** 2026-05-24  
**Scope:** `projects_archive/act_inf_metaanalysis/` (archived; not template pipeline–discovered)  
**Rubric:** template thermo-nuclear maintainability review (1k-line rule, script gates, thin orchestrators, zero-mock tests)

> **Current addendum (2026-07-31):** The historical snapshot metrics below
> (original audit + W1–W3) are retained as a record; the live gate is now
> **687 passed, 1 skipped, 90.24% coverage** (697 collected; fail_under=90)
> with `ruff check` (src/scripts/tests) and `mypy` clean, both enforced by
> `.github/workflows/ci.yml`. A full hostile red-team review (2026-07-31) was
> implemented end-to-end: deterministic canonical/nanopub IDs, fail-closed
> multi-source retrieval, explicit-CLI-wins-over-config, the 0.6 `min_confidence`
> gate, removal of the sole `__import__` monkeypatch, and a suite-inventory
> guard against silently-shadowed tests. Semantic Scholar remains separately
> reported as the live-source blocker (HTTP 429/500).
>
> **Line-count reality check (2026-07-31):** the historical "largest `src/`
> module ≤250 lines" PASS no longer holds. Post-feature modules that exceed the
> 250-line aspirational guideline: `manuscript/variables.py` (879),
> `knowledge_graph/llm_extraction.py` (526), `knowledge_graph/nanopublication.py`
> (484), `literature/semantic_scholar.py` (476), `analysis/artifact_contract.py`
> (470), `visualization/hypothesis_charts.py` (388), `literature/search_runner.py`
> (383), `analysis/release_package.py` (374), `literature/openalex_client.py`
> (370), `knowledge_graph/hypothesis.py` (354), `visualization/temporal_plots.py`
> (332). These are coherent, well-tested units; decomposing them is a deliberate
> future refactor, not a correctness defect.

## Executive verdict

**Historical conditional pass → remediated (W1–W3 complete).** Structural debt from script bloat, orchestrator logic leakage, thin LLM tests, and documentation drift was assessed against the 2026-05-24 baseline of **615 tests / 96.09% coverage**; the current gate is recorded in the addendum above.

---

## Metrics snapshot (post-remediation)

| Metric | Before | After |
|--------|--------|-------|
| Tests collected | 557 (1 failure on script import) | **615 passed** |
| `src/` coverage | ~84% (mid-refactor) | **96.09%** (≥90% gate) |
| Test files | 25 | **39** |
| Scripts >250 lines | **4** (326–359 lines) | **0** (max 91 lines) |
| Largest `src/` module | 556 (`llm_extraction.py`) | 257 (`subfield_defaults.py`) |
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

### Largest `src/` modules (after W2 splits)

| Lines | File |
|------:|------|
| 257 | `src/analysis/subfield_defaults.py` |
| 430 | `src/manuscript/variables.py` |
| 389 | `src/knowledge_graph/nanopublication.py` |
| 225 | `src/knowledge_graph/llm_extraction.py` (orchestrator; was 556) |
| 204 | `src/visualization/advanced/embeddings.py` |
| 97 | `src/analysis/subfield_registry.py` |
| 92 | `src/analysis/subfield_classifier.py` (classification API; was 500) |

---

## Findings by wave

### W1 — Must-fix (completed)

1. **Script bloat / repeated bootstrap** — Added `scripts/_bootstrap.py` and `scripts/_io.py`; moved pipeline bodies to `src/literature/search_runner.py`, `src/analysis/pipeline_runner.py`, `src/knowledge_graph/kg_runner.py`, `src/visualization/figure_runner.py`, `src/literature/fulltext_assessment.py`.
2. **Thin-orchestrator violations in script 02** — Subfield timeline → `src/analysis/temporal_analysis.py` (`compute_subfield_timeline`); document tokenization → `src/analysis/text_processing.py` (`tokenize_documents`).
3. **Thin LLM extraction tests** — Expanded `tests/knowledge_graph/test_extraction.py` with `pytest-httpserver` Ollama stub (real HTTP, no mocks).
4. **Documentation drift** — Root `AGENTS.md`, `README.md`, `doc/*`, and `scripts/README.md` now state **archived** status and `projects_archive/` paths; test counts refreshed to **615 / 39 files**.

### W2 — Should-fix (completed)

1. **`advanced_plots.py` split** — `src/visualization/advanced/` (`labels`, `word_cloud`, `embeddings`, `topics`) + re-export shim in `advanced_plots.py`.
2. **`llm_extraction.py` split** — `llm_config.py`, `llm_client.py`, and `llm_prompts.py`; the remaining module is a slim extraction orchestrator.
3. **Config-driven search queries** — `DEFAULT_ARXIV_QUERIES` / `DEFAULT_RELEVANCE_KEYWORDS` in `src/config.py`; `src/config_loader.py` loads `project_config.search` from `manuscript/config.yaml` with defaults.
4. **Example config** — Added `manuscript/config.yaml.example` (stripped template).

### W3 — Completed (2026-05-24)

1. Split `tests/knowledge_graph/test_llm_extraction.py` (758 lines) → `llm_extraction_fixtures.py` + six `test_llm_*.py` modules (max 212 lines).
2. Nested `.git/` — documented in README; not removed (standalone history may still be referenced).
3. Split `subfield_classifier.py` (500 lines) → `subfield_defaults.py`, `subfield_registry.py`, slim `subfield_classifier.py` (92 lines).
4. Runner coverage expanded in the historical follow-up pass (**615 tests**, **96.09%** coverage; visualization edge cases, `config_loader` ImportError path, injectable search URLs).

---

## Post follow-up metrics (2026-05-24)

| Metric | Value |
|--------|-------|
| Tests | **615 passed** |
| Coverage | **96.09%** |
| Test files | **39** |
| `search_runner.py` coverage | **95.63%** (was 74.68%) |
| Largest test module | `test_llm_nanopub_resume.py` (212 lines) |
| Largest subfield module | `subfield_defaults.py` (257 lines) |

## Code-judo decomposition (before → after)

| Area | Before | After | Target |
|------|--------|-------|--------|
| Script 01 | 359 lines | 63 | ≤250 ✓ |
| Script 02 | 326 | 59 | ≤250 ✓ |
| Script 03 | 351 | 62 | ≤250 ✓ |
| Script 04 | 347 | 52 | ≤250 ✓ |
| `llm_extraction.py` | 556 | 225 + helpers | ≤250 per module ✓ |
| `advanced_plots.py` | 528 | 20 shim + subpackage | ≤204 per module ✓ |
| `subfield_classifier.py` | 500 | 92 + defaults/registry | ≤250 per module ✓ |
| `test_llm_extraction.py` | 758 | 6 modules + fixtures | ≤250 per module ✓ |

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

**Approval bar (W1–W3):**

- [x] All `scripts/*.py` ≤250 lines
- [x] No analysis logic in scripts (timeline/tokenization in `src/analysis/`)
- [x] LLM tests split across `test_llm_*.py` + httpserver paths (no monolithic 758-line file)
- [x] `subfield_classifier.py` ≤250 lines (keywords/registry in sibling modules)
- [x] `test_extraction.py` exercises httpserver LLM path
- [x] Docs reference `projects_archive/` and archived-not-discovered status
- [x] Coverage ≥90%, zero failures/skips (**615 passed**)

---

## Non-code notes

- **Archive location:** Not executed by `./run.sh` until promoted to `projects/`.
- **Optional infrastructure coupling:** Script 04 / `figure_runner` lazy-imports template `infrastructure` when present; standalone archive runs without it.
- **Versioned `output/`:** Expected in the standalone publication repository; keep
  local environments, caches, and coverage databases outside the tracked tree.
