# Review Log — 2026-08-02 (Docs deep review pass)

Repo: `ActiveInferenceInstitute/act_inf_metaanalysis`
Branch: `main` (origin/main @ 19734c9 after force-push reconciliation)
Scope: mega-deep documentation review + implementation. Docs-only pass; no source
or test logic changes unless required to keep the tree green.

## Phase 0 — Preflight

- `git fetch origin` revealed a **force-pushed** `origin/main` (local snapshot
  `985e9ca` was not an ancestor). Working tree was clean, so the authoritative
  remote state was adopted with `git reset --hard origin/main` (`19734c9`).
- Inventory: 982 tracked files (774 under `output/`), 69 tracked markdown files
  (excl. generated `output/`), `doc/` hub with 10 docs + tooling registry,
  root `README.md`, `AGENTS.md`, `CHANGELOG.md`, `TODO.md`, `LICENSE`,
  `.github/workflows/ci.yml`, `manuscript/` (20 sections + config + bib),
  `scripts/` (13 numbered + `z_generate` hydrator + 2 helpers), `src/` (5
  packages, 47 non-init modules), `tests/` (50 files).
- Baseline gate verified live: **688 collected, 687 passed, 1 skipped,
  90.24% coverage** (`uv run pytest tests/ --cov=src --cov-fail-under=90`).
  `ruff check` and `mypy` available via the uv environment.

## Phase 1 — Mega-deep docs review (findings)

All findings below are code-verified against the current tree. They are scoped
into `TODO.md` (section "Docs deep review 2026-08-02") with
`file:line` anchors; every implemented item is marked with a commit reference.

### Major

- **MAJ-D01** — `doc/scripts.md` "Steganographic Hardening" section
  (lines 531–540) describes `secure_run.sh`, `./run.sh`, and
  `infrastructure/steganography/`. None of these exist in this repo; the
  content is a template leftover. Replace with the actual render policy.
- **MAJ-D02** — Root `AGENTS.md` directory tree (lines 51–184) is materially
  stale vs. the current repo: it omits `search_runner.py`, `kg_runner.py`,
  `figure_runner.py`, `pipeline_runner.py`, `llm_config/llm_client/
  llm_prompts.py`, `hypothesis_weights.py`, `provenance.py`, `sensitivity.py`,
  `artifact_contract.py`, `pipeline_manifest.py`, `pilot_protocol.py`,
  `release_package.py`, `snapshot_manager.py`, `tooling_verification.py`,
  `topic_stability.py`, `validation_*.py`, `subfield_defaults/registry.py`,
  `config_loader.py`, `visualization/advanced/`, scripts 07–14, and several
  tests. Rewrite the tree to match reality. The "See Also" section also
  contained monorepo-relative links (`../../AGENTS.md`, `../../projects_archive/`)
  that are dead in the standalone public clone — converted to
  standalone-resolving targets while keeping the `projects_archive/` archive
  context as prose.
- **MAJ-D03** — License contradiction: `README.md:19` badge claims MIT, but
  `LICENSE`, `manuscript/config.yaml:51`, `.aii/config.yaml:49`, and
  `manuscript/README.md:6` all declare **CC-BY-4.0**. Fix the badge + link.

### Medium

- **MED-D01** — Stale test-gate numbers: `src/README.md:5,45` say
  "659 passed / 1 skipped / 90.04%"; `doc/testing.md:7` and
  `doc/CODE_QUALITY_AUDIT.md:9` say "697 collected". Live gate is
  **688 collected / 687 passed / 1 skipped / 90.24%**. Correct all four sites.
- **MED-D02** — `scripts/README.md:102` says "Python 3.10+"; `pyproject.toml:16`
  requires **>=3.12** (README badge already says 3.12+). Fix.
- **MED-D03** — "14 numbered scripts" wording is wrong: there are **13 numbered
  scripts** (01–04, 06–14) plus the canonical `z_generate` hydrator.
  `AGENTS.md:42`, `doc/README.md:28`, `README.md:182` need the corrected count.
- **MED-D04** — `doc/architecture.md` (a) module inventory omits ~25 current
  modules (kg_runner, llm_*, provenance, sensitivity, validation_*,
  artifact_contract, pipeline_manifest, release_package, snapshot_manager,
  tooling_verification, topic_stability, subfield_defaults/registry,
  search_runner, figure_runner, pipeline_runner, fulltext_assessment,
  config_loader); (b) nanopub dedup key is documented as
  `(paper_id, hypothesis_id)` at lines 237 and 396 — the live key includes
  `assertion_type` (MED-07 fix). Update inventory + dedup key.
- **MED-D05** — `doc/hypotheses.md:105` says confidence < 0.5 is "flagged for
  human review"; the validated gate is **0.6** (`min_confidence`, llm_config /
  config.yaml). Also the "How to Add a Custom Hypothesis" YAML example
  (lines 156–160) uses a **list** schema; the real config uses a **dict** keyed
  by H1–H8 under `project_config.hypothesis_definitions`. Fix both.
- **MED-D06** — `doc/scripts.md:8` uses a wrong path
  `projects/archive/_ActiveInference/act_inf_metaanalysis` (inconsistent with
  the canonical `projects_archive/act_inf_metaanalysis`); `doc/scripts.md:82`
  says "12 fields per record" but corpus records have **15 fields**. Fix.
- **MED-D07** — `doc/AGENTS.md` still describes "the 5-stage core chain plus the
  two auxiliary QA scripts (06, 07)" (line 28) and its file-spec list omits
  `ai_meta_analysis_playbook.md`, `CODE_QUALITY_AUDIT.md`,
  `tooling_inventory.yaml`. Update to the 06–14 closure set.
- **MED-D08** — `doc/README.md:226` says api_reference documents "all 5
  packages, 24 modules"; the reference actually covers 25 module sections and
  the src tree has 47 modules. Also the Documentation Index omits
  `ai_meta_analysis_playbook.md` and `tooling_inventory.yaml`. Fix counts, add
  rows.
- **MED-D09** — Quick-start invocation inconsistency: README uses
  `python3 scripts/...`, doc/README and scripts/README use `python scripts/...`,
  playbook/scripts.md use `uv run python scripts/...`. Standardize on
  `uv run python` (uv is the declared environment) and make the
  standalone-vs-monorepo `cd` instruction unambiguous.
- **MED-D10** — Missing code-adjacent docs for a public research repo:
  no `CITATION.cff` (Zenodo DOI 10.5281/zenodo.19461934 exists), no
  `CONTRIBUTING.md`, no `SECURITY.md`. Add grounded versions.

### Minor

- **MIN-D01** — `doc/api_reference.md:431` example uses
  `nanopub_path="output/nanopublications.jsonl"`; the real checkpoint path is
  `output/data/nanopublications.jsonl` (config.yaml:121). Fix example.
- **MIN-D02** — `doc/scripts.md:192` documents `--checkpoint-interval` default
  as `25`; the script default is `DEFAULT_CHECKPOINT_INTERVAL=50`
  (`src/config.py`), with config.yaml setting 25. Clarify the table row.
- **MIN-D03** — `doc/architecture.md:364` says "Checkpointing every 50 papers"
  while the live config is 25; align wording to "configured checkpoint interval
  (25 in `manuscript/config.yaml`; code default 50)".
- **MIN-D04** — `src/SKILL.md:8` says "45+ public APIs"; the api_reference
  documents more than 45 public functions, so the floor claim is safe — leave
  as-is (noted, no change).

## Phase 3 — Implementation

Implemented in logical commits; each TODO entry marked ✓ with its commit.
See `TODO.md` "Docs deep review 2026-08-02" section for the per-item status.

## Phase 4 — Verification

- Re-ran the markdown link/anchor audit after edits (all repo-relative links
  resolve; monorepo-relative links in root `AGENTS.md` are intentional and
  documented as such).
- Test gate re-run after any touched-file changes: 688 collected / 687 passed /
  1 skipped / 90.24% (unchanged).
- Pushed to `origin/main`; verified `git status` clean and up to date.
