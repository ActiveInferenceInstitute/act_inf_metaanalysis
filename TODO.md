# Project TODO

**Status:** forward-only project backlog for minor and medium work plus a
hostile red-team review pass (2026-07-31). New scoped defects from that review
are listed under Minor / Medium / Major below; pre-existing open release items
(MED-01, MED-03, MED-04, MED-05) remain the release-blocking priority.

**Owner:** Active Inference Meta-Analysis project.

**Last reviewed:** 2026-07-31 (hostile deep review + backlog reconciliation).

This is the authoritative project-level backlog. It scopes work that can be
completed without changing the scientific target, hypothesis set, RDF
namespace, or PDF/HTML publication policy. Completed local implementation is
represented by source, tests, and reports rather than by a closed-task list.

## Current baseline (verified 2026-07-31)

Verification was run live against this tree with `uv run pytest --cov=src
--cov-fail-under=90`:

- **1,106** deduplicated papers (`output/data/corpus.jsonl`, 1,105 dated);
- **2,561** provenance-bearing nanopublications (`output/data/nanopublications.jsonl`);
- 16 registered figures (16 PNG + `figure_registry.json`);
- hypothesis scores stable across snapshots (e.g. H4 0.8317, H5 1.0);
- test gate: **686 passed, 1 skipped, 90.06% coverage** after implementing the
  review findings below (fails at 90 gate only if coverage drops below 90);
- the one skipped test is `tests/visualization/test_figure_runner.py:291`
  ("template infrastructure not importable") — see MIN-05.

The release-level external blocker from the 2026-07-26 run is unchanged: the
Semantic Scholar live probe returned a terminal HTTP 429/500 and was recorded
as a failed source; arXiv and OpenAlex completed. No corpus records changed.
A new publication snapshot is not source-complete until all three configured
sources report successful completion in `output/reports/search_provenance.json`
(MED-01).

## Completed / closed backlog (historical closure)

The following items are genuinely done in this tree (code, tests, and reports)
and are retained only as an audit trail. Superseded by the current source.

- Semantic Scholar bounded `Retry-After`/API-key-aware retry diagnostics
  (`src/literature/semantic_scholar.py`) — independently re-verified: the
  `x-api-key` value flows only into the request header and never into logs,
  structured reports, or the `SemanticScholarRateLimitError` message.
- RDF/TriG↔JSONL parity validation and a versioned local release package.
- Release preflight covering artifacts, metadata, renders, and tests
  (`scripts/10_release_preflight.py`).
- Canonical `z_generate_manuscript_variables.py` hydration with token inventory.
- Deterministic full-text and human-calibration queue/protocol preparation
  (`scripts/11_prepare_evidence_pilots.py`).
- Snapshot inventory and safe non-overwriting snapshot copies
  (`scripts/12_snapshot_output.py`).
- Source-backed tooling registry and AI-meta-analysis playbook.
- Dynamic front matter, current-year policy, and release metadata checks.
- Local release-package hash/count verification (`scripts/14_verify_release_package.py`).
- Removal of two untraceable tooling rows; **MED-06** completed locally
  (`output/reports/tooling_verification.json`) — the dated report must simply
  be rerun whenever the publication snapshot is refreshed.

## Pre-existing open release work

These items predate the review and remain the release gate. They are kept as
the primary order of work below.

### MED-01 — Complete the three-source live refresh

**Source:** release blocker confirmed in the 2026-07-26 run.

Retry Semantic Scholar with the configured query set and rate-limit handling.
If new papers are added, rerun deterministic downstream stages and extract
only newly eligible papers with the configured local `gemma3:4b` model.
Preserve the existing snapshot before replacement.

**Done when:**

- `output/reports/search_provenance.json` reports success for arXiv, Semantic
  Scholar, and OpenAlex;
- corpus, analysis, extraction, provenance, figures, variables, and manifest
  agree;
- `scripts/08_validate_artifacts.py` exits 0; and
- Stage 03 and Stage 04 still pass.

**Run rule:** retry without `--clear-corpus` after the source is reachable; use
`--no-resume --clear-corpus` only for an intentionally new dated snapshot.

### MED-03 — Publish the nanopublication artifact

**Source:** GitHub issue #3, "publish nanopubs".

Select a durable external deposit target, then publish the already staged and
locally validated package under the date-stamped output release directory.
Do not publish a partial or source-incomplete snapshot.

**Dependencies:** explicit deposit target and upload authorization.

**Done when:** the deposit contains the exact validated JSONL/TriG files, has a
persistent identifier and version/date, links the repository and license, and
a download-and-verify test reproduces the recorded hashes.

### MED-04 — Run a bounded full-text evidence pilot

**Source:** documented abstract-only extraction limitation.

Use the prepared deterministic queue and a pre-registered open-full-text
sample. Add section-aware quotes and source-location provenance without
changing headline abstract-only scores.

**Dependencies:** full-text access and a human-reviewed fidelity subset.

**Done when:** access failures and exclusions are recorded, quotes retain
locations, the reviewed subset reports fidelity and stance agreement, and pilot
results remain separate from primary corpus results.

### MED-05 — Calibrate LLM extraction against human labels

**Source:** the rule-based study is a reproducibility floor, not human
validation.

Use the prepared stratified calibration queue to create an adjudicated reference
set across hypotheses, stances, subfields, and years. Measure agreement,
precision, recall, F1, quote fidelity, uncertainty, and error categories.

**Dependencies:** human annotation and adjudication.

**Done when:** instructions, blinding, labels, metrics, sample sizes, and the
confidence policy are versioned, and the manuscript describes results as
validation evidence rather than model authority.

## New scoped findings (hostile review, 2026-07-31)

**Implementation status (2026-07-31):** All Major and Medium items below were
implemented and are covered by tests / CI (`ruff check`, `mypy`, pytest with the
90% gate) in the same commit. Most Minor items are also fixed (MIN-01, MIN-02,
MIN-03, MIN-04, MIN-06, MIN-07, MIN-08, MIN-11, MIN-12, MIN-13, MIN-14, MIN-15,
MIN-16, MIN-17, MIN-18). Remaining open items are low-impact polish: MIN-05 (one
template-dependent test skips without the external template repo), MIN-09 (NMF
clamping already emits a warning; optionally fail instead), MIN-10 (optional
`_io.load_json` requirement flag), and the stale `.coverage_review.json`
artifact.

Each item below is a real, code-verified defect with an acceptance gate. They
are independent of the pre-existing release work and can be addressed in any
order; Major items should land before the next publication snapshot.

### Major

- **MAJ-01 — Declared Python support (>=3.10) is violated by 3.12-only syntax.**
  `src/manuscript/variables.py:475` puts a raw backslash string `r'\_'` inside
  an f-string expression; PEP 701 permits this only on Python 3.12+. On 3.10/3.11
  the module fails to import (SyntaxError), so installs that `pyproject.toml`
  (`requires-python = ">=3.10"`) accepts break at runtime. README badge claims
  3.12+, so *three* facts disagree. **Fix:** hoist the escaped literal out of the
  f-string (e.g. `esc = hid.replace("_", "\\_")` before the f-string), and align
  `pyproject.toml` with the actual minimum (3.12).

- **MAJ-02 — `Paper.canonical_id` title-fallback uses Python's process-randomized
  `hash()`.** `src/literature/models.py:98` returns
  `f"title:{hash(self.title.lower().strip())}"`. Builtin `str` hashing is salted
  by `PYTHONHASHSEED` (randomized per process since 3.3), so the fallback ID for
  any paper lacking DOI/arXiv/S2/OpenAlex IDs is **non-deterministic across runs
  and can be negative**. This silently breaks cross-run dedup and incremental
  LLM-extraction resume for ID-less papers, and contradicts
  `src/literature/AGENTS.md` which documents a deterministic sha256-title ID.
  **Fix:** `f"title:{hashlib.sha256(title.lower().strip().encode()).hexdigest()[:16]}"`.
  Same fix should be applied wherever the docs promise title-hash identity.

### Medium

- **MED-07 — `merge_nanopubs` collapses mixed-direction evidence for one
  paper+hypothesis.** Dedup key is `(paper_id, hypothesis_id)`
  (`src/knowledge_graph/nanopublication.py:239-246`). Demonstrated: two
  assertions for the same paper+hypothesis (`supports` + `contradicts`) merge
  to a single record, silently dropping one direction. The schema and the LLM
  recovery path (`llm_extraction.py`) permit multiple directions per
  hypothesis; a re-parse or duplicate assessment therefore biases published
  nanopubs and hypothesis scores with no warning. **Fix:** include
  `assertion_type` (or `assertion_id`) in the merge key, or dedupe by
  `assertion_id` which already encodes `paper_id`+`hypothesis_id`.

- **MED-08 — Nanopublication artifact is not reproducible run-to-run.**
  `nanopub_id = uuid4()` and `created_date` / `processing_date = now()`
  (`nanopublication.py:115,118`, `provenance.py:53-55,65`). A clean
  `--clear-assertions` re-run yields byte-different JSONL/TriG with different
  nanopub URIs, contradicting the project's seed-42 / "deterministic results"
  promise and making DOWNLOAD-AND-VERIFY hash reproducibility of the published
  artifact impossible across regenerations. **Fix:** derive nanopub_id
  deterministically from the assertion (e.g. `sha256(paper_id|hyp_id|type)`),
  and allow an injected snapshot timestamp; keep the RNG-free path for score
  reproduction while permitting explicit re-stamping.

- **MED-09 — Duplicate test class silently disables 4 tests.**
  `tests/literature/test_corpus.py` defines `TestCorpusFilterBySubfield` twice
  (lines 301 and 462). The module attribute resolves to the second definition,
  so the first class's four tests (`test_filter_neuroscience`,
  `test_filter_robotics`, `test_filter_no_matches`,
  `test_filter_returns_new_corpus`, lines 301-354) are **never collected**.
  This is a silent false-confidence hole in the 90% coverage gate. **Fix:**
  rename the shadowed class or merge the two; add a guard so collected test
  count is asserted (see MIN-06).

- **MED-10 — CLI flags are silently overridden by config.yaml.**
  `scripts/02_meta_analysis_pipeline.py` advertises `--n-topics`,
  `--max-features`, `--min-year`, `--seed`, but `pipeline_runner.py:53-56`
  unconditionally replaces them from `manuscript/config.yaml`; likewise
  `search_runner.py:196-199` overwrites `args.query`/`--max-results` from config.
  A user who sets `--seed 0` or `--query ...` gets a different value with no
  warning — a reproducibility hazard for a published pipeline. **Fix:** honor an
  explicitly-passed flag or fail with a clear message when a CLI value differs
  from the config value.

- **MED-11 — `bootstrap_project` resolves the template repo from CWD and
  ancestors.** `scripts/_bootstrap.py:22-39` walks `Path.cwd()` and parent
  directories looking for any `infrastructure/` dir and imports the first
  match. Import behavior therefore depends on the invoking directory and a
  stray `infrastructure/` dir anywhere up the tree silently shadows the intended
  template root — a determinism and mild supply-chain hazard. **Fix:** require
  `TEMPLATE_REPO_ROOT` (or a local `template` path) and fail explicitly if the
  intended root is absent; do not scan arbitrary parents.

- **MED-12 — LLM endpoint port is inconsistent across config and docs.**
  `manuscript/config.yaml:127` sets `base_url: http://localhost:11435` (and two
  `worker_urls` at 11435), while `src/config.py:70`, `llm_config.py:12`, and
  `scripts/AGENTS.md` all document the default as 11434. Config wins at runtime,
  so this is not a live bug, but the contradiction is a reproducibility hazard
  for anyone standing up a fresh Ollama on the documented port. **Fix:** pick
  one port everywhere; anchor the docs/README/AGENTS to the config value.

- **MED-13 — A single malformed nanopub line aborts the whole stage.**
  `deserialize_nanopubs` (`nanopublication.py:203-219`) and
  `nanopub_from_dict` raise on any malformed/partial JSONL record, so one
  corrupt line prevents every downstream stage from loading. No per-line
  skip-and-report exists. **Fix:** on a bad line, log the error with line
  number, skip it, and mark the run resumable; or fail with a precise
  line-numbered message rather than a trace-back of the first byte.

- **MED-14 — Lint/type gates are not enforced and the tree does not pass.**
  `ruff check` reports 8 errors in `src/` (including MAJ-01's invalid-syntax,
  unused imports, E741 ambiguous `l` in `hypothesis_charts.py:327`), 39 in
  `scripts/` (E402 bootstrap pattern), 3 in `tests/`; `ruff format --check`
  would reformat 83 files; `mypy src/` reports 146 errors (many missing-stub /
  import-path environmental, but at least `llm_extraction.py:398` and
  `field_overview.py:142` are real type defects). No `ruff`/`mypy` config or CI
  gate exists in `pyproject.toml`, so quality claims in AGENTS.md/README are not
  enforced. **Fix:** add `[tool.ruff]`/`[tool.mypy]` config, resolve or
  `noqa`-the-bootstrap E402s, and add a lint CI check; pin the Python floor (see
  MAJ-01) so the invalid-syntax error is unambiguous.

- **MED-15 — OpenAlex and arXiv retry only 429/5xx, not transport errors.**
  `openalex_client._request_with_retry` (`:174-217`) and `arxiv_client._fetch_page`
  (`:185-204`) propagate `requests.ConnectionError`/`Timeout` immediately,
  unlike Semantic Scholar (`semantic_scholar.py:180-193`). A flaky network
  fails the whole source instead of retrying. **Fix:** add
  `(ConnectionError, Timeout)` to the retry set in both clients with the
  existing bounded backoff.

- **MED-16 — OpenAlex fails *soft* on rate limit; S2 fails *closed*.**
  `search_openalex` catches `HTTPError` and `break`s (`openalex_client.py:271-273`),
  returning a truncated paper list that `search_runner` records as a successful
  source. Semantic Scholar uses `raise_on_error=True` (`search_runner.py:149`)
  and flags the source failed. A rate-limited OpenAlex call can silently thin
  the corpus while the gate reports success. **Fix:** raise on terminal 429 (or
  record `success:false` + partial marker) to match the S2 fail-closed policy.

- **MED-17 — Highest-risk paths have no test coverage despite the green gate.**
  Verified against `term-missing` output: `hypothesis_weights.py` — the
  `RAW_CITATION`/`CONFIDENCE_ONLY`/`AGE_DISCOUNT`/`FIELD_NORMALIZED` policies are
  untested (uncovered lines 50,67,110,115,156), yet they feed
  `hypothesis_sensitivity.json`; `llm_extraction.py` resume-safety guards
  (incompatible model/prompt/pipeline raise ~294, multiple-run-ID raise ~299,
  min_confidence filter 174-175, per-paper failure, checkpoint/interrupt flush,
  multi-worker) are untested; `kg_runner.py` **incomplete-coverage `RuntimeError`
  abort (126) and missing-coverage guard (132)** are untested — the most
  safety-critical code in the pipeline. Additionally `temporal_plots.py:139-142`
  **re-implements CAGR**, duplicating `temporal_analysis.estimate_growth_rate:161`
  (two sources of truth for a headline number) with neither copy under real test.
  **Fix:** add policy tests, a resume-mismatch test (real tiny HTTP / synthetic
  nanopubs), a kg_runner coverage-abort test, and a full H1–H8/`STANDARD_HYPOTHESES`
  order cross-check; de-duplicate the CAGR implementation.

- **MED-18 — `test_config_loader.py` monkeypatches `builtins.__import__` — the
  suite's only mock, violating the no-mock policy.**
  `tests/test_config_loader.py:90-103` fakes a missing `yaml` via
  `monkeypatch.setattr(builtins, "__import__", blocked_import)`, which
  `tests/AGENTS.md` explicitly forbids; it also protects only `config_loader`
  while the identical fallback in `hypothesis.py:111-113` stays uncovered.
  **Fix:** inject a yaml-loadable param or run a clean subprocess; drop the mock.

- **MED-19 — `min_confidence` code default is 0.0 while the validated/configured
  gate is 0.6, and AGENTS justifies 0.6 with a misleading κ claim.**
  `llm_config.py:22` defaults `min_confidence=0.0`; `kg_runner.py:41` falls back
  to 0.0 when the key is absent, silently bypassing the 0.6 threshold that
  `config.yaml:135` sets. Separately, `knowledge_graph/AGENTS.md` cites a
  "κ > 0.70 requirement", but the real pipeline-vs-rule-reference κ is −0.048
  (0.704 is only the rule-rule stability). **Fix:** make 0.6 the dataclass and
  runner default; reword AGENTS to state κ=0.704 is rule-rule stability and
  pipeline-reference κ is −0.048.

### Minor

- **MIN-01 — CAGR reads the full `year_counts` dict instead of `bounded_counts`.**
  `estimate_growth_rate` (`temporal_analysis.py:155-156`) uses
  `year_counts[...]` after bounding by `end_year` via `bounded_counts`. Values
  coincide because the dicts map the same years to the same counts, so this is
  currently correct, but it is fragile and a future change to bounded aggregation
  would silently corrupt the CAGR endpoint. Use `bounded_counts`.

- **MIN-02 — Neutral assertions have no hypothesis triple in the KnowledgeGraph.**
  `graph_builder.py` (`add_assertion`) emits a supports/contradicts edge only;
  neutral assertions get no predicate link, whereas the nanopub RDF export
  (`nanopublication.py:371`) DOES emit `aif:neutral`. The two RDF models
  disagree, and neutral assertions are not queryable-by-hypothesis through the
  graph. Add a `neutral` link (and include it in `ASSERTION_TYPES` counts) or
  document the divergence explicitly.

- **MIN-03 — `get_assertions_for_paper` performs a linear scan per paper.**
  The rdflib branch (`graph_builder.py:262-269`) walks all of `_assertion_map`
  for every paper. Fine at the current corpus scale, but an easy O(N²) trap for
  query loops. Build a `paper_id -> [assertion_id]` index.

- **MIN-04 — Stale comment in `detect_communities`.**
  `citation_network.py:162-163` says "Remove isolated nodes … add them back
  after" but isolate removal is not implemented; isolates become singleton
  communities. Make the comment match the code or implement the described
  removal.

- **MIN-05 — One test is skipped because template infra is not importable.**
  `tests/visualization/test_figure_runner.py:291` skips when
  `infrastructure.documentation.figure_manager` is unavailable, so figure
  registration is never exercised in this archived/standalone location. Either
  vendor/pin the template import or assert it is present in CI.

- **MIN-06 — No test asserts the collected test count.**
  MED-09 (the shadowed class) went unnoticed precisely because no invariant
  locks the suite size. Add a collection-time assertion (e.g. a doctest/`--co`
  check) that the total collected count is the documented value, so silent
  test loss is caught immediately.

- **MIN-07 — LLM port / worker duplication in config.**
  `manuscript/config.yaml:128-130` lists the identical URL twice in
  `worker_urls`, which spawns two threads against one Ollama endpoint for no
  benefit. Drop the duplicate or make the number of workers intentional.

- **MIN-08 — `as_of_date` silently falls back to `date.today()` when unset.**
  `pipeline_runner.py:79-82` uses `date.today()` if config has no `as_of_date`,
  making the CAGR endpoint non-deterministic across runs if the frozen date is
  ever removed. Require the frozen date or warn loudly.

- **MIN-09 — NMF topic count is silently clamped.**
  `topic_modeling.py:115` clamps `n_topics` to `min(n_topics, n_docs,
  n_features)`, which on a small corpus yields fewer topics than the `{{NUM_TOPICS}}`
  variable and the figure registry expect. Emit a clear warning (or fail) when
  clamping occurs.

- **MIN-10 — `_io.load_json` returns `{}` silently on a missing artifact.**
  `scripts/_io.py:11-19` logs a warning and returns an empty dict, so callers
  proceed with vacuous data if an upstream artifact is absent. For
  release-path artifacts prefer a hard failure (matches the hydration gate).

- **MIN-11 — `temporal_trend`/`temporal_trend_with_counts` are duplicated and
  `temporal_trend` is effectively dead.**
  `hypothesis.py:282-354` has two near-identical implementations; ruff flags an
  unused `temporal_trend` import in `kg_runner.py:16`. Consolidate on
  `_with_counts` and drop the dead variant + import.

- **MIN-12 — `snapshot_manager.copy_snapshot` is not atomic.**
  `snapshot_manager.py:59` `shutil.copytree` writes straight to the final
  destination; an interrupt leaves a partial snapshot and a same-label rerun
  raises `FileExistsError`. Copy to a temp dir then `rename`.

- **MIN-13 — `release_package.prepare_release_package` silently overwrites a
  prior staged package.** `shutil.copyfile` (`release_package.py:182-184`) writes
  over existing files in a reused `nanopublications-<as_of_date>/` dir — unlike
  snapshot_manager's explicit no-overwrite guard — so a partially-failed prior
  run can leave stale files that get hashed into the new manifest. Clear or
  reject an existing package dir before staging. (The hash/count verifier itself
  is correct.)

- **MIN-14 — OpenAlex DOI and URL assembly lacks validation in two spots.**
  `openalex_client.py:327` interpolates `doi` raw into
  `f"{base_url}/works/https://doi.org/{doi}"` with no quoting (exported but not
  on the live path; `urlquote` it and reject `/`, whitespace, control chars);
  `openalex_client.py:284` extends `all_papers` without the S2-style
  `[:remaining]` slice, so an over-returning API can overshoot `max_results`.

- **MIN-15 — `test_temporal_plots.py:11-90` are pure smoke tests.**
  They assert only file-exists/`st_size>0`/PIL size; no axis, title, or
  **CAGR/N/median annotation text** is asserted, so a silent mis-render of the
  headline CAGR label passes. Assert on collected figure text/artists.

- **MIN-16 — `test_hypothesis.py:173` (`test_hand_computed_score`) is
  tautological.** The expected value is built by re-typing the exact production
  formula on the same inputs, so a systematic bug (dropped neutral, sign flip,
  mis-weight) is invisible. Assert against independently-derived edge values.

- **MIN-17 — The H1–H8→hypothesis_id alias map is duplicated and under-tested.**
  `variables.py:486-495` hardcodes the mapping that `hypothesis.STANDARD_HYPOTHESES`
  order (implicitly) defines; tests only check H1 and H3 (lines 487,496), so a
  reorder/desync of H2/H4–H8 passes. Add a full 8-way cross-check or derive the
  aliases from `STANDARD_HYPOTHESES`.

- **MIN-18 — Minor prose/artifact drift.**
  (a) `output/manuscript/00_abstract.md:5` frames CAGR as "across 2000–2026"
  but it is computed over **2003–2025** — reword to the observed empirical span;
  (b) `CHANGELOG.md:53` records "655 collected / 654 passed / 90.07%" for the
  same date every other doc cites as **660 / 659 / 90.04%** — correct it;
  (c) `.coverage_review.json` reports a stale 94.18% (2026-04-29) vs the current
  90.04% gate — refresh or annotate; (d) `ASSERTION_SUPPORT_PCT="95.8"` is
  computed over non-neutral assertions only (1751/1828) — rename to
  `NON_NEUTRAL_SUPPORT_PCT` or document the denominator so future prose cannot
  misuse it as a share of all 2,561.

## Order of work

1. **MED-01:** resolve the incomplete Semantic Scholar source; this is the sole
   release blocker and publishes the current scientific results.
2. **MAJ-01, MAJ-02, MED-07, MED-08, MED-09:** fix the version contract and the
   data-integrity / reproducibility / test-collection defects before the next
   snapshot is frozen, since they affect the published artifact and the gate's
   trustworthiness (MAJ-02 also governs cross-run dedup and resume identity).
3. **MED-10..MED-19:** robustness (transport retries, fail-closed OpenAlex,
   min_confidence default), gate enforcement (lint, no-mock), and coverage gaps;
   land before treating the pipeline as "clean".
4. **MED-03 / MED-04 / MED-05:** external deposit and validation pilots after the
   primary source-complete snapshot is frozen.
5. **Minor items:** fold in opportunistically; MIN-01, MIN-06, MIN-08 affect
   determinism and should precede any reproducibility assertion.

## Release gate

The project is ready for a minor/medium-work release when all applicable items
above have acceptance evidence, coverage remains at or above 90%, the artifact
contract exits 0, all configured literature sources complete, the 16-figure
registry is consistent, all manuscript variables resolve, both PDF and HTML
render/validation pass, the local package verifier passes, and the tooling
verification is either fully verified or explicitly resolved by the owner. A
passing render does not override an incomplete source or tooling gate.

## Explicitly deferred larger work

Adding hypotheses, changing the ontology namespace, replacing the local
extraction model, building a public query/RAG service, expanding the literature
domain, or changing the primary abstract-only estimand to a corpus-wide
full-text estimand requires a separate design and scope decision.