# Project TODO

**Status:** forward-only project backlog for minor and medium work.

**Owner:** Active Inference Meta-Analysis project.

**Last reviewed:** 2026-07-25.

This is the authoritative project-level backlog. It scopes work that can be
completed without changing the scientific target, hypothesis set, RDF
namespace, or PDF/HTML publication policy. Completed local implementation is
represented by source, tests, and reports rather than by a closed-task list.

## Current baseline

The frozen 2026-07-24 snapshot contains:

- 1,106 deduplicated papers; 1,071 eligible papers processed;
- 2,561 provenance-bearing nanopublications;
- eight configured NMF topics with seed 42 as the primary fit;
- 16 registered figures;
- successful PDF and HTML render/validation stages;
- 651 collected tests: 650 passed, one skipped, 91.12% coverage against the
  90% gate.

The remaining release-level defect is external: Semantic Scholar returned HTTP
429 during the latest live retrieval. arXiv and OpenAlex completed. The
artifact contract and pipeline manifest retain this failure deliberately. A
new publication snapshot is not source-complete until all three configured
sources report successful completion.

## Completed local closure

The following minor/medium implementation surfaces are complete and should be
treated as current project infrastructure:

- Semantic Scholar bounded `Retry-After`/API-key-aware retry diagnostics;
- RDF/TriG↔JSONL parity validation and a versioned local release package;
- release preflight covering artifacts, metadata, renders, and tests;
- canonical `z_generate_manuscript_variables.py` hydration with token inventory;
- deterministic full-text and human-calibration queue/protocol preparation;
- snapshot inventory and safe non-overwriting snapshot copies;
- source-backed tooling registry and AI-meta-analysis playbook;
- dynamic front matter, current-year policy, and release metadata checks.
- local release-package hash/count verification before any external deposit;
- dated tooling-source probing with explicit repository/license/activity flags;
- removal of two untraceable legacy tooling rows from the publication table.
- release preflight integration for the tooling verification gate;
- self-reference-free inventory/manifest generation verified stable across a
  repeated run;
- final portable namespace table cleanup, leaving Stage 04 with no markdown
  diagnostics.

## Medium work

### MED-01 — Complete the three-source live refresh

**Source:** release blocker identified in the 2026-07-24 run.

Retry Semantic Scholar with the configured query set and rate-limit handling.
If new papers are added, rerun deterministic downstream stages and extract
only newly eligible papers with the configured local `gemma3:4b` model. Preserve
the existing snapshot before replacement.

**Done when:**

- `output/reports/search_provenance.json` reports success for arXiv, Semantic
  Scholar, and OpenAlex;
- corpus, analysis, extraction, provenance, figures, variables, and manifest
  agree;
- `scripts/08_validate_artifacts.py` exits 0; and
- Stage 03 and Stage 04 still pass.

**Run rule:** retry without `--clear-corpus` after the source is reachable; use
`--no-resume --clear-corpus` only for an intentionally new dated snapshot.

**Latest attempt (2026-07-25):** the S2-only resume-safe retry exhausted four
bounded retries after 132.4 seconds with HTTP 429. A broad all-source retry was
aborted after arXiv timed out/returned 429, before it could overwrite the
successful arXiv/OpenAlex status. The current search provenance therefore
retains the known S2 blocker and the existing 1,106-paper snapshot.

### MED-03 — Publish the nanopublication artifact

**Source:** GitHub issue #3, “publish nanopubs”.

Select a durable external deposit target, then publish the already staged and
locally validated package under `output/release/nanopublications-2026-07-24/`.
Do not publish a partial or source-incomplete snapshot.

**Dependencies:** explicit deposit target and upload authorization.

**Done when:** the deposit contains the exact validated JSONL/TriG files, has a
persistent identifier and version/date, links the repository and license, and
a download-and-verify test reproduces the recorded hashes.

**Local closure completed:** the staged package now has a manifest-hash/count
verification gate (`scripts/14_verify_release_package.py`). External deposit
selection, credentials, and persistent identifier remain unprovided.

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

### MED-06 — Complete external tooling verification

**Source:** GitHub issue #4, “include tooling analysis”.

Complete the dated external checks for the retained entries in
`doc/tooling_inventory.yaml`: canonical repository/documentation URL,
release/version, license, and access/activity status. The publication-facing
table and bibliography-backed evidence identifiers are already registry-backed.

**Done when:** every retained row has a dated check, stale/dead or unlicensed
entries are flagged or removed, and the rendered PDF/HTML remains legible.

**Latest local probe (2026-07-25):** `output/reports/tooling_verification.json`
checked all 19 retained rows; 3 repository-backed rows verified fully and 16
were flagged for paper-only sources, stale activity, missing licenses, or a
transient GitHub API rate limit. The report is intentionally fail-closed.

The tooling report is now included in `scripts/10_release_preflight.py` and
`output/reports/pipeline_manifest.json`; release readiness therefore remains
blocked until the flagged rows receive an owner decision and primary-source
verification.

## Minor work

No locally actionable minor item remains after the 2026-07-25 closure pass.
Add a new item here only with a concrete acceptance gate, owner, and project
scope.

## Order of work

1. **MED-01:** resolve the incomplete Semantic Scholar source.
2. **MED-03:** select a target and publish the validated local package.
3. **MED-04 / MED-05:** run full-text and human-calibration pilots after the
   primary source-complete snapshot is frozen.
4. **MED-06:** complete the external tooling verification pass.

## Release gate

The project is ready for a minor/medium-work release when all applicable items
above have acceptance evidence, coverage remains at or above 90%, the artifact
contract exits 0, all configured literature sources complete, the 16-figure
registry is consistent, all manuscript variables resolve, and both PDF and HTML
render/validation pass. The local package verifier must also pass, and tooling
verification must be either fully verified or explicitly resolved by the
project owner. A passing render does not override an incomplete source or
tooling gate.

## Explicitly deferred larger work

Adding hypotheses, changing the ontology namespace, replacing the local
extraction model, building a public query/RAG service, expanding the literature
domain, or changing the primary abstract-only estimand to a corpus-wide
full-text estimand requires a separate design and scope decision.
