# CHANGELOG.md

## Unreleased — completion interruption consistency (2026-11-16)

- Classify zero-assertion outcomes before publishing paper completion and
  checkpoint only zero-result IDs whose completion was committed. SIGINT
  between those updates can repeat an uncommitted assessment but cannot
  strand resume with a missing-assertion completion receipt.
- Add deterministic real-SIGINT regressions at both completion-update
  boundaries using the existing loopback HTTP extraction fixture.
  This repair does not acquire corpus evidence or change scientific outputs.
- Feed the declared manuscript preamble into the HTML LaTeX reader so custom
  mathematical macros expand before MathML conversion, with a real-Pandoc
  regression covering the manuscript's notation. Apply the admitted conclusion
  corrections about proposed bibliography ingestion and existing quote fields.
  Both PDF and HTML readers explicitly accept LaTeX `\(...\)` / `\[...\]`
  math delimiters as well as dollar-delimited Markdown math.

## Unreleased — focused source-contract acceptance (2026-11-13)

This entry records governed local evidence for the preserved isolated lane at
base `c09f537f6ed4406828ff29c38003cbddecb39a32`, not a new scientific snapshot,
installed release, hosted CI result, or full-suite/coverage qualification.
The dated entries below remain historical evidence.

- **F1 — Existing-sample validation.** `--no-auto-labels` consumes
  `output/validation/sample.csv` without resampling or rewriting it. Primary
  human labels are required; secondary human labels are optional. Missing,
  empty, or invalid annotations fail. Automatic mode remains deterministic
  rule-reference labeling and refuses to overwrite existing annotations.
  Reports distinguish `reference_kind: human` from
  `reference_kind: deterministic_rule_based`, and
  `kappa_interannotator` from `kappa_interrule`; accepted metrics are mirrored.
  Existing rule-labeled manuscript results are not human validation.
- **F2 — Semantic package parity.** Strict JSONL decoding and graph-aware RDF
  isomorphism compare assertion, provenance, head, and publication content,
  not just IDs. Equivalent RDF serialization is accepted; duplicate IDs,
  altered content, and unexpected graphs fail before an existing staged
  package is replaced. The resumed source restores the missing
  `deserialize_nanopubs` import used by package verification.
- **F3–F5 / AM-N1 — Independent render inputs and destination.**
  `--input-root ROOT` selects existing `ROOT/data/manuscript_variables.json`,
  `ROOT/figures/figure_registry.json`, and figure files.
  `--manuscript-dir DIR` owns the manuscript sources and `references.bib`;
  `--output-root ROOT` independently selects the PDF/HTML build destination
  and `reports/render_receipt.json`. Referenced figures are staged as local
  assets beside each rendered surface, without replacing a figures directory
  with a symlink. Actual Pandoc conversion retains semantic tables, longtables,
  citations, bibliography, and MathML; HTML conversion warnings fail the render.
  Each PDF render runs BibTeX after the first XeLaTeX pass, followed by two
  XeLaTeX passes, including when reusing a build directory. Off-repository
  output paths are recorded as absolute paths.
  The title/front matter is a Pandoc raw-LaTeX block separated from the
  manuscript Markdown: TeX grouping braces no longer print as text, and the
  following Results heading remains semantic Markdown. The actual PDF
  regression rejects those leaks; all three regenerated regression pages were
  visually inspected. This is fixture-only rendering evidence, not a rebuilt
  scientific publication. Actual HTML browser verification remains unavailable:
  the governed browser could not initialize its sandbox; no sandbox bypass was
  used. Authored References-heading ownership remains a publication decision.
- **F6 / F10 — Completion and cancellation custody.** Version-1 paper-completion
  receipts retain processed paper IDs and `zero_assertion_paper_ids` with
  run/model/prompt/pipeline provenance admission. Accepted assertions are
  persisted before completion receipts; resume rejects incompatible provenance
  or missing positive evidence. Count-only historical receipts cannot identify
  zero-result completions and are not upgraded by inventing paper IDs.
  `--clear-assertions` explicitly removes completion sidecars. Failed and
  unprocessed counts are disjoint. Cancellation stops dispatch and retries,
  cancels pending work, and checkpoints accepted results before waiting for
  active HTTP requests to finish or reach their configured transport timeout;
  it does not forcibly terminate an active request. An all-zero completed run
  does not bypass nonempty release-evidence requirements.
- **F7 — Effective analysis provenance.** `analysis_run.json` records effective
  execution settings, including an explicit seed of zero, for the primary NMF
  fit and stability analysis. Artifact validation and the manifest consume
  that execution receipt while retaining frozen configuration separately.
  Historical outputs do not acquire an invented execution receipt.
- **F8 / F9 — Full publication-source completeness.** arXiv, Semantic Scholar,
  and OpenAlex are all required even when a run requests fewer sources.
  Every recorded arXiv query must succeed; a later successful query cannot hide
  an earlier failure. Artifact validation, the manifest, and manuscript
  variables share this interpretation; release preflight retains the artifact
  gate. These regressions do not resolve the live-source release blocker.
- **F11 / F12 / MIN-11.** Positive-to-zero terminal growth returns CAGR `-1`
  while retaining existing zero-start and endpoint policies. An explicitly
  empty or invalid `TEMPLATE_REPO_ROOT` fails infrastructure admission;
  unset-root discovery and standalone operation remain distinct.
  `temporal_trend` now projects scores from `temporal_trend_with_counts`,
  preserving exact cumulative scores/counts and exclusion behavior.
- **Documentation-only corrections.** MIN-19 now states the existing
  `(paper_id, hypothesis_id, assertion_type)` merge key. The conclusion no
  longer advertises an unimplemented bibliography importer or describes
  already-stored evidence fields as future work. Importer approval, full-text
  research, human quote review, calibration, and publication authorization
  remain open; no hypothesis, score, label, or generated artifact was changed
  by these documentation corrections.

### Recorded commands, bindings, and limits

Both receipts are GitVault `test`-classification launches, using CPython 3.15.2
and imports selected from the isolated lane. The following path abbreviations
transcribe the recorded `ACTUAL_COMMAND` arrays, including the first command's
repeated output options; they are not additional executions:

```bash
G=/Users/friedman/Documents/Git/gitvault
PY="$G/Username/ActiveInferenceInstitute/Public/act_inf_metaanalysis/.venv/bin/python"
C="$G/Local/execution-launches/resume-federation-metaanalysis-contracts-05c4e277/64159-0378b23fcd404cf19d581613b6f946ad"
R="$G/Local/execution-launches/resume-federation-metaanalysis-fixed-959f7f89/64305-7e43a8f29e92468e8fe1f65356e701aa"
cd "$G/Local/worktrees/aii-implement-act_inf_metaanalysis-20261113"
"$PY" -B -m pytest --no-cov -p no:cacheprovider -q \
  --basetemp="$C/outputs/cases" --junitxml="$C/outputs/regressions.xml" \
  tests/analysis/test_validation_cli.py \
  tests/test_quality_remediation.py::test_validation_metrics_on_labeled_rows \
  tests/test_quality_remediation.py::test_validation_metrics_quote_fidelity_na_when_no_quotes \
  tests/analysis/test_release_package.py tests/test_render_publication.py \
  tests/knowledge_graph/test_llm_completion.py \
  tests/knowledge_graph/test_llm_interrupt.py \
  tests/knowledge_graph/test_llm_nanopub_resume.py \
  tests/knowledge_graph/test_llm_max_papers.py \
  tests/knowledge_graph/test_llm_batch.py tests/knowledge_graph/test_kg_runner.py \
  tests/analysis/test_pipeline_runner.py tests/analysis/test_topic_modeling.py \
  tests/analysis/test_temporal_analysis.py tests/analysis/test_artifact_contract.py \
  tests/analysis/test_pipeline_manifest.py tests/analysis/test_source_status.py \
  tests/test_bootstrap.py tests/knowledge_graph/test_hypothesis.py \
  -p no:cacheprovider --basetemp="$C/outputs/cases" \
  --junitxml="$C/outputs/junit.xml"
"$PY" -B -m pytest --no-cov -q \
  tests/analysis/test_release_package.py tests/test_render_publication.py \
  -p no:cacheprovider --basetemp="$R/outputs/cases" \
  --junitxml="$R/outputs/junit.xml"
```

- First receipt (`C`): **155 passed, 5 failed**, exit 1. The failures were two
  missing-import package checks, two incidental Pandoc title-casing assertions,
  and a renderer fixture lacking an author. The passing validation, completion,
  interruption, effective-settings, source-status, growth, bootstrap, and
  hypothesis cohorts supply the focused evidence for F1, F6–F12, and MIN-11.
- Repaired receipt (`R`): **20 passed**, exit 0, after restoring the import,
  correcting the synthetic author fixture, and removing only the incidental
  title-casing assertion. This supplies focused package and real-render evidence
  for F2–F5 and AM-N1. The overlapping cohorts are not summed.
- Source SHA-256 in `C/verified.json`:
  `51fb59981bfab337b417c137e6c5bf133ac7a4f936e383ffc4872e19ddfef727`;
  in `R/verified.json`:
  `097ea208292d2cd81257ecb2512b9346bd75b55a139b43d29b7c574495b3a903`.
  Both `exit.json` receipts record unchanged bound inputs and reaped children.
  Each `intent.json` preserves the exact named-input SHA-256 values; each
  `stdout.raw`, `exit.json`, and `outputs/junit.xml` preserves the command and
  outcome. These bindings predate the documentation edits, not a new
  whole-repository qualification.
- Real Pandoc/XeLaTeX/BibTeX regressions exercised HTML tables/longtables,
  citations, bibliography, staged images, relative and absolute external roots,
  and PDF text after changing citations and bibliography in a reused build.
  Fixture render receipts are under `R/outputs/cases/` at
  `test_html_retains_tables_citat0/external-render/reports/render_receipt.json`,
  `test_html_retains_tables_citat1/external-render/reports/render_receipt.json`,
  and `test_repeated_pdf_render_refre0/external-render/reports/render_receipt.json`;
  their surface paths are absolute. These are controlled regression fixtures,
  not a refreshed scientific manuscript. **Parent visual inspection of the
  actual HTML/PDF remains pending.**

No full CI, installed-runtime, full-suite/coverage, live research, human
calibration, or scientific qualification is claimed. Frozen inputs/outputs,
dated receipts, configuration pins, rights, and approval holds are unchanged.

## Unreleased — Publishing member migration

- Register the documented gate arms in `.aii/config.yaml`, repair sidecar guide
  paths, and identify the docs index, manuscript command, and GNN pin there.
- Point to the lead Publishing contract; carry its identity schema and checker
  unchanged, with recorded digests checked by `./run.sh docs` alongside the
  existing GNN pin. Existing member gate implementations remain authoritative.

## Unreleased — one gate entry point, documentation index, and manuscript render (2026-11-12)

The repository had three scattered gate commands in CI, no local runner, no
documentation link check, no fast test selection, and no render command at all
even though `output/pdf/` and `output/web/` were committed. This entry records
the consolidation.

- **`./run.sh` is the single gate entry point.** Arms: `lint`, `types`,
  `test-fast` (default), `test-full`, `docs`, `gnn`, `render`, `all`, `bench`.
  The commands live once in `scripts/gate.py`; `.github/workflows/ci.yml` calls
  the same arms instead of repeating commands.
- **CI is one job with one environment.** The separate `gnn-conformance` and
  `test` jobs each did their own checkout and Python setup; the workflow now
  syncs once and runs `./run.sh lint|types|docs|gnn|test-full`. The pinned GNN
  parser installation moved into `scripts/gnn_conformance.py`, which caches
  `.gnn-env` per pin revision.
- **Fast test selection uses a registered marker.** `slow` marks the
  figure-generation tests; `./run.sh` runs `pytest -m "not slow"` and the full
  arm keeps the 90% coverage gate.
- **Documentation check and index.** `scripts/check_docs.py` verifies relative
  links, heading anchors, and that `docs/documentation-index.md` lists every
  long-lived guide. `docs/README.md` is the hub and
  `docs/documentation-index.md` is the flat index; the long-form guides remain
  in `doc/` so committed manifest hashes stay valid.
- **Measured arm times live in `docs/_generated/gate_arms.md`**, regenerated by
  `./run.sh bench`; the receipt records the pre-consolidation baseline too.
- **Manuscript render.** `scripts/15_render_publication.py` hydrates the source
  sections from `output/data/manuscript_variables.json`, validates
  `output/figures/figure_registry.json` against the included figures, and runs
  pandoc → XeLaTeX → BibTeX → XeLaTeX to `output/pdf/` and `output/web/`.
  `./run.sh render` renders into `.render-check/`.
- **Two render blockers fixed.** `manuscript/preamble.md` now loads `hyperref`
  explicitly before `\hypersetup` (pandoc 3.13 inserts header includes earlier
  than the template's hyperref load), and a `references.bib` comment containing
  `@misc` made BibTeX abort at that line; the comment is reworded.
- **Manuscript gate claims corrected.** The methods and tooling appendix no
  longer cite a 60% infrastructure coverage gate (there is no infrastructure
  package) and no longer claim tests run on every push; the documented gate is
  the 90% branch-coverage gate on `src/`, executed locally.
- **Documentation updated with the estate facts**: `docs/README.md` records the
  `.github/gnn-pin.json` schema (`gnn-importer-pin/v1`), revision
  `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`/`v5.0.3`, and that the conformance
  check is the `Pinned GNN conformance` step in the workflow's single `gate`
  job (display name `gate (lint, types, docs, gnn, tests)`); the workflow does
  not use the `ActiveInferenceInstitute/.github` `setup-python-uv` composite
  action.

## Unreleased — CI gate repair: dev tools declared, lint rule set stated (2026-11-01)

The workflow runs `ruff check src/ scripts/ tests/` and `mypy src/`, but neither
tool was declared in the `dev` extra, so every run on `main` since 2026-08-01
failed at the lint step in 15–22 seconds (`error: Failed to spawn: ruff`). The
documented development setup in `CONTRIBUTING.md` names the same three gates, so
the declaration was the missing piece.

- **`pyproject.toml`** — the `dev` extra now declares `ruff>=0.6.0` and
  `mypy>=1.10.0`, matching the documented commands.
- **`pyproject.toml`** — the lint gate states its rule set explicitly
  (`select = ["E4", "E7", "E9", "F"]`), which is the classic default the
  configuration comment already described. Without it a newer ruff release
  silently widens the gate: ruff 0.17.3's wider defaults report 199 findings on
  this unchanged tree, all outside the documented rule set.
- **`uv.lock`** — regenerated for the two added tools.
- **Verified on this tree**: `uv run ruff check src/ scripts/ tests/` → "All
  checks passed!"; `uv run mypy src/` → "Success: no issues found in 60 source
  files"; `uv run pytest tests/ --cov=src --cov-fail-under=90` → 687 passed,
  1 skipped, 90.05% coverage.

## Unreleased — GNN structural sketches for H1, H4, and H8 (2026-11-01)

Added `gnn/`, three illustrative GNN (Generalized Notation Notation) models that
make the generative-model structure behind three Standard Hypotheses explicit and
machine-readable: a boundary-maintaining system for `H1` (`FEP_UNIVERSALITY`),
prediction error minimization for `H4` (`PREDICTIVE_CODING`), and predictive
language comprehension for `H8` (`LANGUAGE_AIF`).

Claim boundary, unchanged by this addition: the sketches are documentation. They
carry no corpus numbers, contribute no evidence to any score, are read by no
script, and change no artifact contract, manifest, release package, or manuscript
variable. `STANDARD_HYPOTHESES` order and the H1–H8 aliases are untouched, and
`doc/hypotheses.md` gains only a pointer to the sketches.

- **Illustrative parameters only.** Every parameter is an example value (round
  likelihoods, uniform or near-uniform priors) so no number can be misread as an
  estimate from the corpus. Each file states its own limitations in
  `ModelAnnotation`: for H4 the hierarchical direction of predictive coding is
  not represented, and for H8 the sketch takes no position on the explanatory-gain
  question its contradicting evidence raises.
- **Machine-checked structure.** All three sketches parse and type-check with the
  real GNN pipeline at revision `v5.0.3`
  (`8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`): step 3 `SUCCESS` with 3 of 3 files
  parsed, 0 failures, 66 serialized formats; step 5 `SUCCESS` with 3 of 3 files
  valid, 0 errors, 0 warnings. The digests the pipeline recorded for the consumed
  models are listed in `gnn/README.md` for re-checking with `shasum -a 256`.
- **Documentation duality.** `gnn/README.md` (human index, claim boundary, worked
  examples) and `gnn/AGENTS.md` (agent constraints, verification procedure) follow
  the repository's per-directory pair standard; `README.md`, `AGENTS.md`,
  `doc/README.md`, `doc/hypotheses.md`, `TODO.md`, and the `.aii` sidecar link to
  the new directory.
- **No new dependencies.** The repository gains no GNN dependency; the sketches
  are plain Markdown with no vendored code.
- **Gate.** Documentation-only addition, so no source line is added or removed:
  `uv run pytest --cov=src --cov-fail-under=90 -v` → **687 passed, 1 skipped,
  90.05% coverage**, exit 0. (The 2026-07-31 baseline in `TODO.md` records 90.24%
  from a different environment; nothing in this change can move coverage.)

## Unreleased — hostile red-team review closure (2026-07-31)

Applied the findings of a full hostile deep review of the tree. Test gate now
**687 passed, 1 skipped, 90.24% coverage**; `ruff check` and `mypy` are clean
and enforced in a new CI workflow.

- **Reproducibility / data integrity.** Title-fallback `canonical_id` now uses a
  deterministic sha256 digest instead of the process-randomized builtin `hash()`
  (`models.py`), so ID-less papers keep a stable cross-run identity. Nanopub IDs
  are now derived deterministically from `(paper_id, hypothesis_id, assertion_type)`
  (stable RDF/JSONL across re-runs), and `merge_nanopubs` no longer collapses
  mixed-direction (supports + contradicts) evidence for one paper+hypothesis.
- **Python contract.** `pyproject.toml` now declares `requires-python = ">=3.12"`
  to match the PEP 701 syntax actually used (the f-string backslash in
  `variables.py` that broke 3.10/3.11 is rewritten).
- **Fail-closed retrieval.** OpenAlex and arXiv now retry transport errors;
  OpenAlex fails *closed* on a terminal HTTP error (matching Semantic Scholar)
  so a rate-limited source can no longer silently thin the corpus. OpenAlex DOI
  lookups URL-quote their argument.
- **CLI over config.** Explicit `--query/--max-results/--n-topics/--max-features/
  --min-year/--seed` flags are honored over `manuscript/config.yaml` instead of
  being silently overwritten.
- **Robustness.** `bootstrap_project` prefers `TEMPLATE_REPO_ROOT`/project-local
  template and logs any fallback scan; a malformed nanopub line now fails with a
  precise `file:line` instead of an opaque trace-back; `min_confidence` defaults
  to the validated 0.6; the LLM port documented in code/`scripts/AGENTS.md`
  matches config (`11435`).
- **Test/infra hardening.** A duplicate test class that silently shadowed 4
  corpus tests is fixed; a suite-inventory test (AST) guards against recurrence;
  tests added for weight policies, the 0.6 confidence gate, H1–H8 alias order,
  fail-closed OpenAlex, transport retries, and malformed-nanopub errors; the sole
  `unittest`-style `__import__` monkeypatch was removed (no-mock policy). Added
  `ruff`/`mypy` config and `.github/workflows/ci.yml`.
- **Second polish pass.** Fixed MIN-02 (neutral assertions get a `neutral`
  hypothesis triple in the KnowledgeGraph, matching the RDF export), MIN-03
  (O(1) paper→assertion index), MIN-08 (warn when `as_of_date` is unset),
  MIN-12 (atomic snapshot copy via temp dir + rename), MIN-13 (release staging
  clears stale files before re-staging), MIN-15 (real CAGR/N/median annotation
  text assertions with extracted helpers), and MIN-18 (documented the
  `ASSERTION_SUPPORT_PCT` non-neutral denominator and decoupled the abstract
  CAGR claim from the inclusion window).

## Semantic Scholar retrieval hardening (earlier working-tree state, 2026-07-26)

- Switched literature search to the provider's bulk continuation-token endpoint,
  with a local result cap because the provider may over-return rows.
- Split bulk-search fields from detail fields so unsupported nested references
  are not requested from the bulk endpoint; detail and citation calls retain
  their full field sets.
- Added documented `x-api-key` and user-agent headers, bounded retries for
  transient 429/5xx and transport failures, and structured secret-safe terminal
  429 diagnostics.
- Preserved fail-closed source provenance: a terminal 429 or 5xx is recorded as
  a failed source, never as a successful empty search. The current live provider
  probe remains externally blocked by HTTP 500; the corpus was not changed.
- Standardized package, manuscript, documentation, and user-agent URLs on the
  public repository `ActiveInferenceInstitute/act_inf_metaanalysis`.
- Removed the obsolete root PDF `act_inf_metaanalysis_v2_04-30-2026.pdf` and
  published the current validated render as the date-stamped
  `act_inf_metaanalysis_v2.0.6_2026-07-26.pdf`.
- Promoted the complete current `output/` tree into the public repository;
  generated data, figures, manuscript, HTML/PDF renders, reports, validation
  records, release packages, and snapshots are now versioned for reproducibility.

## v2.0.6 — 2026-07-24

### Full-refresh reproducibility and resumability
- Centralized pipeline version, prompt version, NMF (`n_topics=8`, seed 42), render formats, current-year/YTD policy, and repository metadata in the project configuration.
- Added atomic extraction state and run-ID-preserving resume semantics. A checkpointed run refuses to mix model, prompt, or pipeline versions; the JSONL checkpoint remains authoritative for processed paper IDs.
- Added topic-stability analysis, yearly hypothesis assertion counts, direct nanopublication provenance recomputation, cross-artifact validation, and a hash/count/gate pipeline manifest.
- Established `scripts/z_generate_manuscript_variables.py` as the sole manuscript hydration entrypoint with source-token inventory, artifact hashes, and unresolved-token failure.
- Corrected temporal handling for partial current-year data, citation-network top-100/full-graph labeling, figure layout metadata, stale manuscript claims, and template-sensitive LaTeX constructs.
- The July 24 live refresh was intentionally stopped after its durable checkpoint (517 assertions across 200 of 1,071 eligible papers); it is resumable and is not publication-complete until extraction, figures, hydration, and PDF/HTML gates pass.

### 2026-07-25 closure addendum
- Completed the local idempotent closure pass: release-package hashes/counts, tooling-source verification, cross-artifact gates, canonical manuscript hydration, and self-reference-free snapshot/manifest reruns.
- Re-rendered and validated the 64-page PDF and HTML manuscript with exactly 16 registered figures; PDF/HTML are enabled while slides, DOCX, and EPUB remain explicitly disabled.
- The prior snapshot recorded the local test gate and live-source blockers; the
  current gate and current source status are superseded by the 2026-07-26
  addendum below.
- Stabilized citation-network reruns by canonicalizing community/tie ordering,
  using a fixed HITS start vector, and rounding serialized ranking values; the
  deterministic downstream repeat now produces zero changed artifacts.

### 2026-07-26 MED-06 and render closure addendum
- Completed registry-owned external verification for all 18 retained tooling
  rows, with dated source, release/version, license, reachability, and activity
  observations; row-level limitations remain explicit in the report.
- Removed the unresolvable adaptive federated-learning repository from the
  publication-facing tooling table and recorded its traceable preprint as an
  excluded candidate.
- Refreshed the configured snapshot date, manuscript variables, PDF, HTML, and
  template validation reports. The current gate is 655 collected tests, 654
  passed, 1 skipped, and 90.07% coverage.
- Stage 03 and Stage 04 both exit 0 with PDF/HTML enabled and slides, DOCX, and
  EPUB disabled. Semantic Scholar HTTP 429 remains the only live source gate
  failure.

## v2.0.4 — 2026-07-23

### Completed the v2.0.3 honest-reframe work (in-flight test/artifact gaps)
- **`analysis.validation_sample` had zero test coverage** (0.00%, 73/73 statements uncovered) despite being the module the validation-study runner depends on. Added `tests/analysis/test_validation_sample.py` (6 tests: year-bin boundaries, stratified-sample stratum coverage, fixed-seed determinism, empty-corpus edge case, CSV round-trip). Project coverage rose 93.01% → 94.96% (626 → 632 tests passing).
- **`output/reports/extraction_provenance_summary.json` was stale**, still showing a pre-v2.0.3 schema (`total: 1490`, prior pipeline attribution, and zero structured provenance) even though the clean three-layer re-extraction had already populated real provenance blocks on all 793 current nanopublications. Because the report's schema did not match what `manuscript.variables` reads (`unique_models` / `prompt_versions`), `{{PROV_MODEL}}` / `{{PROV_PROMPT_VERSION}}` in `02b_methods_extraction.md` were unresolved and variable injection raised `RuntimeError`. Regenerated the report via the existing `provenance.write_provenance_summary` (no LLM call needed — pure aggregation over the already-re-extracted nanopub file): it now reports `gemma3:4b` / `v2.0.0-three-layer` across all 793 records; injection succeeds cleanly (348 variables across 18 files).
- **Verified idempotency**: `scripts/07_run_validation_study.py` and `scripts/z_generate_manuscript_variables.py` each produce byte-identical output across two consecutive runs against the same pipeline data (seed=42 stratified sampling; deterministic rule protocols).
- **`data/validation/annotation_schema.md` was a missed call-site of the v2.0.3 reframe**: still titled "Dual-Annotator Validation Schema" and documenting the old fabricated design (`labels_human.csv` / `labels_assistant.csv`, `human_triage` / `assistant_triage` columns, "Human gold labels"). Rewrote it to document the actual current schema (`labels_rule_reference.csv`, `ref_*` / `secondary_*` columns, both deterministic rule protocols) and state plainly this is not a human study.
- **A repo-wide exhaustive literal sweep (`annotator`, `dual`, `inter-rater`, `kappa`, `agreement`) surfaced two more missed call-sites in `manuscript/05_appendix_tooling.md`**: prose stating "Inter-annotator agreement (κ) is computed when multiple annotators assess the same paper" (present tense, describing a live per-assertion mechanism that does not exist) and a quality-thresholds table row enforcing "Inter-annotator κ ≥ 0.70 → Re-annotate" (a fictional gate — no re-annotation loop exists, and the real measured κ is negative, nowhere near 0.70). Reframed both to describe the actual offline rule-based reference-annotator check, reported not enforced. Also tightened the `98_symbols_glossary.md` κ definition to name the rule-reference-vs-pipeline usage instead of a bare "inter-annotator agreement" that reads as human annotation in isolation.
- **Added a proof-of-detection test for `analysis.validation_metrics.classify_error`** (`test_classify_error_detects_each_known_bad_case`): asserts the function actually fires the correct taxonomy code on six planted defect shapes (over-extraction, direction inversion, quote mismatch, triage mismatch, evidence-status/type mismatch) plus the well-formed no-error case — this taxonomy previously had no direct unit test, only indirect exercise via aggregate metrics.
- Removed 4 residual unused imports (`dataclasses.field` in `provenance.py`; `compute_sensitivity_analysis` / `inject_variables` in `test_quality_remediation.py`) flagged by `ruff check` on the touched files; `mypy` clean on all validation/provenance/sensitivity modules.
- Full suite: 633 passed, 95.18% coverage, single final run at a stable tree (no partial re-runs).

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
No public API changes.

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
- **M5**: Former NMF topic-count note removed; the publication-facing configuration is now `k=8` with fixed alternate-seed topic-stability checks.
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
