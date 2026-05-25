# CHANGELOG.md

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
