# CHANGELOG.md

## v2.0.4 — 2026-07-23

### Completed the v2.0.3 honest-reframe work (in-flight test/artifact gaps)
- **`analysis.validation_sample` had zero test coverage** (0.00%, 73/73 statements uncovered) despite being the module the validation-study runner depends on. Added `tests/analysis/test_validation_sample.py` (6 tests: year-bin boundaries, stratified-sample stratum coverage, fixed-seed determinism, empty-corpus edge case, CSV round-trip). Project coverage rose 93.01% → 94.96% (626 → 632 tests passing).
- **`output/reports/extraction_provenance_summary.json` was stale**, still showing the pre-v2.0.3 legacy schema (`total: 1490`, `legacy_attribution: {pipeline_v1: 1490}`, zero structured provenance) even though the clean three-layer re-extraction had already populated real provenance blocks on all 793 current nanopublications. Because the report's schema didn't match what `manuscript.variables` reads (`unique_models` / `prompt_versions`), `{{PROV_MODEL}}` / `{{PROV_PROMPT_VERSION}}` in `02b_methods_extraction.md` were unresolved and variable injection raised `RuntimeError`. Regenerated the report via the existing `provenance.write_provenance_summary` (no LLM call needed — pure aggregation over the already-re-extracted nanopub file): now reports `gemma3:4b` / `v2.0.0-three-layer` across all 793 records; injection succeeds cleanly (348 variables across 18 files).
- **Verified idempotency**: `scripts/07_run_validation_study.py` and `scripts/05_inject_variables.py` each produce byte-identical output across two consecutive runs against the same pipeline data (seed=42 stratified sampling; deterministic rule protocols).
- **`data/validation/annotation_schema.md` was a missed call-site of the v2.0.3 reframe**: still titled "Dual-Annotator Validation Schema" and documenting the old fabricated design (`labels_human.csv` / `labels_assistant.csv`, `human_triage` / `assistant_triage` columns, "Human gold labels"). Rewrote it to document the actual current schema (`labels_rule_reference.csv`, `ref_*` / `secondary_*` columns, both deterministic rule protocols) and state plainly this is not a human study.
- Removed 4 residual unused imports (`dataclasses.field` in `provenance.py`; `compute_sensitivity_analysis` / `inject_variables` in `test_quality_remediation.py`) flagged by `ruff check` on the touched files; `mypy` clean on all validation/provenance/sensitivity modules.
- Full suite: 632 passed, 94.96% coverage, single final run at a stable tree (no partial re-runs).

## v2.0.3 — 2026-07-22

### Clean three-layer re-extraction (structured provenance end-to-end)
- **Re-ran LLM assertion extraction over the full corpus with the three-layer prompt.** Every nanopublication now carries populated source-claim text, a verbatim evidence quote, evidence status/type, and a **structured provenance block** (model ID, prompt version, processing date, run ID). All prior data was cleared before re-extraction; there is no mixed-schema data remaining.
- Fixed a config-precedence bug in `kg_runner`: an explicit `--clear-assertions` CLI flag is no longer silently overridden by `config.yaml`'s `clear_assertions: false`.
- `extraction_provenance_summary.json` now reports real model/prompt/run coverage and the processing-date range; the vacuous `unknown` aggregation is gone.
- `quote_fidelity_rate` is measured against real evidence quotes; when a sample contains no quotes it reports `null` + `quote_fidelity_status` rather than a misleading `0.0`.

### Honest extraction-agreement study (no fabricated human validation)
- **Reframed the extraction validation as a rule-based reference-annotator agreement study, not a human validation.** The "annotator" labels are produced by deterministic keyword rules (`apply_primary_rule_protocol` / `apply_secondary_rule_protocol`), never by humans. Renamed metric keys (`kappa_interrule`, `kappa_reference_pipeline`, `confusion_reference_vs_pipeline`) and CSV columns (`ref_*` / `secondary_*`); the runner writes one `labels_rule_reference.csv` instead of two identical files that falsely implied independent annotators.
- Resolved the prior internal contradiction: abstract, methods, results, and conclusion no longer claim validation "against primary human labels"; all consistently describe the rule reference as a reproducibility floor and state that human gold-standard annotation is future work.
- Sensitivity `sign_flip_count` (structurally always 0 for [0,1] scores) replaced with a real `rank_change_count`.
- New tests pin these invariants; full suite green.

## v2.0.2 — 2026-07-22

### Quality remediation
- Enforced post-2000 corpus filter at load/save; removed two 1977 contaminants (`CORPUS_SIZE` = 817 aligned with citation/subfield counts)
- Three-layer extraction model: source claim, evidence supply, hypothesis triage
- Structured extraction provenance on every nanopublication; summary report under `output/reports/`
- Six weight-policy sensitivity analysis with `hypothesis_sensitivity.json`
- Stratified rule-based reference-annotator agreement study (`n=200`); metrics injected as `VAL_*` template variables (reframed honestly in v2.0.3 — the reference is deterministic keyword rules, not human annotation)
- Manuscript language tempered to evidence-mapping / triage; Zenodo metadata generated from injectors

## v2.0.1 — 2026-04-29

### Summary
Patch release: fixes 5 retry-path bugs in literature clients, syncs documentation
with the current 819-paper corpus, and re-runs LLM extraction so nanopublications
cover every eligible paper. 558/558 tests pass at 94.76 % coverage.

### Bug Fixes
- **arxiv_client.py** — `delay_override` is now plumbed through `_fetch_page`;
  the previous `NameError` raised on every transient HTTP error is gone
- **openalex_client.py** — `_request_with_retry` accepts `delay_override` and
  no longer raises `UnboundLocalError` when retries exhaust
- **semantic_scholar.py** — same fix as openalex; 429 retries succeed cleanly
- **manuscript/__init__.py** — replaced absolute `from manuscript.variables`
  with the correct relative import (broke any external `import src.manuscript`)
- **knowledge_graph/__init__.py** — `query.py` is now exported in `__all__`
  alongside the rest of the public API
- **scripts/03_build_knowledge_graph.py** — incremental LLM extraction is now
  honoured: the script previously skipped extraction whenever ANY nanopubs
  existed, leaving newly retrieved papers permanently un-extracted

### Test Fixes
- `test_search_http_error` and `test_retry_on_*` (openalex + semantic_scholar)
  rewrote the broken `pytest.raises(Exception)` wrappers that masked the
  source-side bugs above

### Data Refresh
- LLM re-extraction filled the 745→748 paper coverage gap (gemma3:4b, ~6 min);
  nanopublications grew from 1487 → 1490; hypothesis scores stable to 3 dp
- 16 figures, 304 manuscript variables, and the combined 2.96 MB PDF all
  regenerated against the current corpus

### Documentation Updates
- `doc/architecture.md` — corpus size 849 → 819 (817 with usable year)
- `doc/scripts.md` — Stage 6 (`06_fulltext_assessment.py`) documented
- `doc/api_reference.md`, `doc/data_formats.md` — added `pdf_url`,
  `is_open_access`, `full_text_source` to the `Paper` schema
- `doc/testing.md` — test count and coverage figure aligned with CHANGELOG
- Project root `README.md` — Quick Start now lists scripts 05 and 06
- Manuscript abstract — hard-coded domain percentages replaced with
  `{{<>}}` placeholders, `{{NUM_TOPICS}}` plumbed through, sparse-citation
  caveat ("only 7.4 % reference resolution") made explicit
- Manuscript hypothesis section — H8 reframed as "near-consensus boundary"
  at 0.83; consensus tier scoped to 5 hypotheses to remove the contradictory
  six-vs-boundary framing
- Stale `manuscript_combined.txt` (5 weeks old) removed from project root

---

## v2.0.0 — 2026-04-28

### Summary
Minor update with critical bug fixes, robustness improvements, and pipeline infrastructure modernization. All 558 tests pass with 94.75% coverage.

### Breaking Changes
None — fully backward compatible.

### New Features
- Centralized configuration: all hardcoded paths and constants now live in `src/config.py`
- Strict variable injection by default (`lenient=False`) — fails fast on unresolved template variables

### Bug Fixes (Critical)
- **C1**: Version metadata corrected — package now reports `2.0.0` (was incorrect `0.1.0`)
- **C4**: Output directory fully untracked in git — `.gitignore` updated; `output/` now disposable
- **C5**: HITS algorithm exception handling — errors now logged at ERROR level with sentinel labels; no more silent empty results
- **C6**: Pipeline rerun with all fixes applied; stale metrics corrected across documentation
- **H3**: Division-by-zero guard in CAGR calculation (handles `start_count == 0`)
- **H8**: `_load_json()` now returns `{"_error": "file_not_found: <path>"}` sentinel; downstream code checks sentinel before use

### Improvements
- **H4**: Variable injection strict by default — raises `RuntimeError` on any `{{VAR}}` placeholders remaining after substitution
- **H5**: LLM JSON parse retry logic — 2 attempts with 2s exponential backoff; raw response logged at DEBUG on failure
- **H6**: Confidence-filter logging — per-paper INFO logs and run-level summary of filtered assertions
- **H7**: Configuration centralization — `src/config.py` consolidates all paths and magic numbers; 6 pipeline scripts updated to import
- **H2**: Manuscript disclaimers — abstract and conclusion now explicitly state assertions are machine-generated without human validation
- **M3**: Cross-section table verification note added ("verified against pipeline run output dated 2026-04-28")
- **M4**: Assertion error rate disclosure — methods now state current corpus lacks validation set; error rates unquantified
- **M5**: NMF topic count justification documented ("k=5 selected via silhouette analysis across k ∈ {2,…,10}")
- **M7**: Recency bias limitation acknowledged in Discussion — citation weighting underweights recent papers
- **M8**: Domain A2 over-classification acknowledgment moved to Discussion Limitations with explicit H1 impact statement

### Test Enhancements
- **M2**: Visualization tests now validate image content (PIL size checks, non-blank assertion via matplotlib) in addition to file existence
- **M6**: Subfield classifier tests refactored from 30+ individual functions to single parameterized test with descriptive IDs
- **M1**: Removed 3 unused `unittest.mock.patch` imports that violated "no mocks" policy

### Documentation Updates
- Corrected corpus size throughout: N = **819 papers** (previously inconsistent 849 in some places)
- Corrected assertion count: **1,487 assertions** from 745 papers (previously stale 2,795)
- All pipeline outputs regenerated with fixed codebase

### Testing
- All 558 tests pass
- Coverage: 94.75% (threshold: 90%)
- Test runtime: ~37s

### Infrastructure
- `.gitignore` expanded to exclude `output/`, `*.egg-info/`, `.pytest_cache/`, `.venv/`, `dist/`, `build/`
- Removed 250+ previously tracked output artifacts from git index

---

**Commit range:** (next commit will be the full v2.0.0 release)
**Released by:** Hermes Agent + Claude Code audit & dispatch
**Zenodo DOI:** 10.5281/zenodo.19461934
