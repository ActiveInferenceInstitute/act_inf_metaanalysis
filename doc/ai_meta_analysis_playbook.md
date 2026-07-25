# AI-driven meta-analysis playbook

This project is a reproducible evidence-mapping pipeline, not an automated
scientific-claims generator. The local model classifies abstract-level evidence
against a fixed hypothesis set; scores are citation-weighted triage signals and
must not be presented as confirmation.

## 1. Freeze the run configuration

Work from the archived project directory:

```bash
cd projects_archive/act_inf_metaanalysis
uv sync --extra dev
```

Treat `manuscript/config.yaml` as the single configuration source. Before a new
snapshot, deliberately update `analysis.as_of_date`, then preserve the prior
`output/` tree under `output/snapshots/<UTC_TIMESTAMP>/`.

The live policy is PDF and HTML only, NMF `n_topics: 8`, primary seed `42`, and
the current year is included in totals/plots but excluded from CAGR when it is
partial. The configured extraction model is local Ollama `gemma3:4b`.

## 2. Retrieve and deduplicate the corpus

For a new snapshot, run all configured sources:

```bash
uv run python scripts/01_literature_search.py --config manuscript/config.yaml \
  --no-resume --clear-corpus
```

The search report records each source, query, retry outcome, counts, and error.
HTTP 429 is a failed source, not an empty successful result. A retry of an
interrupted source can use `--force-search` with the existing corpus and should
not use `--clear-corpus`.

## 3. Compute deterministic analysis

```bash
uv run python scripts/02_meta_analysis_pipeline.py --log-level INFO
```

This writes the subfield totals, temporal metrics, TF-IDF/NMF topics, topic
stability diagnostics, and full citation graph. Re-running this stage replaces
only derived artifacts and must converge deterministically for the same input
hash and configuration.

## 4. Extract assertions with resumable local inference

Start the configured local Ollama listener in a separate terminal, then run:

```bash
uv run python scripts/03_build_knowledge_graph.py --config manuscript/config.yaml \
  --clear-assertions --checkpoint-interval 25
```

Every checkpoint records a single run ID, model, prompt version, pipeline
version, processing dates, and paper coverage. If interrupted, restart without
`--clear-assertions`; processed paper IDs are skipped. Do not mix model,
prompt, or pipeline versions within a run.

## 5. Generate figures and hydrate the manuscript

```bash
uv run python scripts/04_generate_figures.py --dpi 300
uv run python scripts/z_generate_manuscript_variables.py --project .
```

The hydrator writes the exact source-token inventory and artifact hashes to
`output/data/manuscript_variables.json`. It fails on unresolved uppercase
tokens. Do not hand-edit `output/manuscript/`.

## 6. Run QA and closure

```bash
uv run python scripts/06_fulltext_assessment.py --output-dir output
uv run python scripts/07_run_validation_study.py --output-dir output
uv run python scripts/08_validate_artifacts.py
uv run python scripts/09_write_pipeline_manifest.py \
  --render-status pass --validation-status pass
uv run python scripts/10_release_preflight.py
uv run python scripts/11_prepare_evidence_pilots.py
uv run python scripts/12_snapshot_output.py
uv run python scripts/13_verify_tooling_inventory.py
uv run python scripts/14_verify_release_package.py
```

The rule-based validation study is a reproducibility floor, not human
validation. The evidence-pilot queues are intentionally blank until human
annotators supply labels and source locations. The release preflight runs the
test/coverage gate, validates RDF/TriG parity, checks metadata, verifies PDF
and HTML presence, and records all blocking checks.

The tooling probe is intentionally fail-closed: it reports the subset of
retained tools with an explicitly reachable, licensed, non-archived repository
and flags paper-only or stale entries for review. The release-package verifier
proves local hashes before any future external deposit is attempted.

## 7. Render through the template

Use the template's Stage 03 render and Stage 04 validation after hydration.
The configured render block must remain:

```yaml
pdf: true
html: true
slides: false
docx: false
epub: false
```

A passing render does not override a failed source-completion or extraction
gate. The final status is the conjunction of source, extraction, artifact,
preflight, render, validation, and test gates.

## Recovery rules

- **Source rate limit:** retain the corpus, retry the source with configured
  backoff/API access, and rerun downstream stages only if new papers arrive.
- **Interrupted Ollama extraction:** resume from the atomic JSONL checkpoint;
  never delete it unless a deliberate full re-extraction is being started.
- **Artifact mismatch:** inspect `artifact_contract.json` and repair the
  upstream stage; do not patch generated output by hand.
- **Render failure:** quarantine stale failed render outputs, rerun hydration,
  and inspect the TeX/HTML diagnostics before rerunning Stage 04.
- **Disk pressure:** preserve source/manuscript files and remove only explicitly
  selected rebuildable output snapshots.

## Scientific boundaries

The primary estimand is abstract-level evidence mapping across the configured
retrieval snapshot. Full-text availability does not imply full-text extraction.
LLM stance labels can be unsupported or directionally wrong; provenance and
human calibration are required before treating them as publishable annotations.
The citation graph resolves only references whose identifiers match a corpus
record. Partial-year counts are descriptive YTD values, not complete-year
comparisons.
