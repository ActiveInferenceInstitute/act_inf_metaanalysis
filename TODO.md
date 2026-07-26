# Project TODO

**Status:** forward-only project backlog for minor and medium work.

**Owner:** Active Inference Meta-Analysis project.

**Last reviewed:** 2026-07-26.

This is the authoritative project-level backlog. It scopes work that can be
completed without changing the scientific target, hypothesis set, RDF
namespace, or PDF/HTML publication policy. Completed local implementation is
represented by source, tests, and reports rather than by a closed-task list.

## Current baseline

The current 2026-07-26 snapshot contains:

- 1,106 deduplicated papers; 1,071 eligible papers processed;
- 2,561 provenance-bearing nanopublications;
- eight configured NMF topics with seed 42 as the primary fit;
- 16 registered figures;
- successful PDF and HTML render/validation stages;
- 659 collected tests: 658 passed, one skipped, 90.02% coverage against the
  90% gate.

The remaining release-level defect is external: Semantic Scholar returned HTTP
429 during the latest live retrieval. arXiv and OpenAlex completed. The
artifact contract and pipeline manifest retain this failure deliberately. A
new publication snapshot is not source-complete until all three configured
sources report successful completion.

The local Semantic Scholar implementation is now hardened: bulk continuation
tokens, local result caps, documented `x-api-key` delivery, bounded retries for
429/5xx and transport failures, secret-safe terminal diagnostics, and source
provenance status capture are covered by the project test gate. The provider
returned HTTP 500 after the 2026-07-26 bounded retry during the follow-up live
probe; no corpus records changed. The external source gate remains open until
the provider returns a successful bulk response.

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
- complete dated tooling-source probing with registry-owned canonical URLs,
  release/version, license, reachability, and activity observations;
- removal of two untraceable tooling rows from the publication table.
- release preflight integration for the tooling verification gate;
- self-reference-free inventory/manifest generation verified stable across a
  repeated run;
- deterministic citation ranking/community serialization verified stable across
  repeated Stage 02 and downstream runs;
- final portable namespace table cleanup, leaving Stage 04 with no evidence
  registry errors or non-critical Markdown URL notes.

## Medium work

### MED-01 — Complete the three-source live refresh

**Source:** release blocker confirmed in the 2026-07-26 run.

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

**Latest attempts (2026-07-26):** the S2-only resume-safe retry exhausted four
bounded attempts after 132.4 seconds with HTTP 429, then the bulk-endpoint
follow-up exhausted four bounded attempts after 88.6 seconds with HTTP 500.
Both attempts preserved the existing 1,106-paper snapshot and recorded failure
provenance rather than treating the source as an empty success. Re-run with
`--force-search` after provider recovery; do not clear the corpus for a retry.

### MED-03 — Publish the nanopublication artifact

**Source:** GitHub issue #3, “publish nanopubs”.

Select a durable external deposit target, then publish the already staged and
locally validated package under the date-stamped output release directory.
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

### MED-06 — Complete external tooling verification — complete locally

**Source:** GitHub issue #4, “include tooling analysis”.

Complete the dated external checks for the retained entries in
`doc/tooling_inventory.yaml`: canonical repository/documentation URL,
release/version, license, and access/activity status. The publication-facing
table and bibliography-backed evidence identifiers are registry-backed.

**Done when:** every retained row has a dated check, stale/dead or unlicensed
entries are flagged or removed, and the rendered PDF/HTML remains legible.

**Completed local probe (2026-07-26):** `output/reports/tooling_verification.json`
checked every retained row from the registry using the canonical source URL.
Repository metadata, releases/tags or package versions, license files or
declared license evidence, reachability, and activity are recorded per row.
Source-only, stale, restricted, and unlicensed entries remain explicitly
flagged; the overall report passes only when every row has a complete dated
observation. The dead adaptive federated-learning repository was removed from
the retained publication inventory and recorded as an excluded candidate with
its traceable paper identifier.

The tooling report is included in `scripts/10_release_preflight.py` and
`output/reports/pipeline_manifest.json`. Row-level flags remain visible in the
report and manuscript; they do not become unqualified software claims.

## Minor work

No locally actionable minor item remains after the 2026-07-26 closure pass.
Add a new item here only with a concrete acceptance gate, owner, and project
scope.

## Order of work

1. **MED-01:** resolve the incomplete Semantic Scholar source.
2. **MED-03:** select a target and publish the validated local package.
3. **MED-04 / MED-05:** run full-text and human-calibration pilots after the
   primary source-complete snapshot is frozen.
4. **MED-06:** complete locally; retain the dated report and rerun it whenever
   the publication snapshot is refreshed.

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
