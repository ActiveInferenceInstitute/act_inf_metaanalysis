# Scripts — Active Inference Meta-Analysis Pipeline

Project-specific orchestrator scripts for the Active Inference literature meta-analysis. Each script is a **thin orchestrator** that coordinates I/O and sequencing; all logic lives in `../src/`.

## Quick Start

```bash
# From the project root (projects_archive/act_inf_metaanalysis/ in the monorepo, or the repository root in a standalone clone)
cd /path/to/template/projects_archive/act_inf_metaanalysis

# 1. Retrieve literature corpus (default: merge into existing corpus.jsonl; use --no-resume to ignore it)
uv run python scripts/01_literature_search.py

# 2. Run quantitative analyses
uv run python scripts/02_meta_analysis_pipeline.py

# 3. Build knowledge graph (requires Ollama for LLM extraction)
uv run python scripts/03_build_knowledge_graph.py --llm-model gemma3:4b

# 4. Generate publication figures
uv run python scripts/04_generate_figures.py --dpi 300

# 5. Hydrate manuscript variables through the canonical template entrypoint
uv run python scripts/z_generate_manuscript_variables.py --project .

# 6. Assess full-text availability
uv run python scripts/06_fulltext_assessment.py

# 7. Deterministic validation / QA
uv run python scripts/07_run_validation_study.py --sample-fraction 0.10 --min-size 200
uv run python scripts/08_validate_artifacts.py
uv run python scripts/09_write_pipeline_manifest.py
uv run python scripts/11_prepare_evidence_pilots.py
uv run python scripts/12_snapshot_output.py
uv run python scripts/13_verify_tooling_inventory.py
uv run python scripts/10_release_preflight.py
uv run python scripts/14_verify_release_package.py
```

Scripts `01`–`04` plus the canonical `z_generate_manuscript_variables.py` entrypoint form the core content-generation chain (run in order). Scripts `06`–`09` close QA, cross-artifact validation, and provenance. Scripts `11`–`13` prepare review queues, snapshots, and tooling-source evidence; Script `10` then runs the non-LLM release preflight and refreshes the final manifest. Script `14` verifies the staged package.

## Pipeline Overview

| # | Script | Purpose | Duration |
|---|--------|---------|----------|
| 01 | `01_literature_search.py` | Multi-API corpus retrieval (arXiv, S2, OpenAlex) | ~5 min (first run) |
| 02 | `02_meta_analysis_pipeline.py` | TF-IDF, NMF topics, citation network, temporal analysis | ~30 sec |
| 03 | `03_build_knowledge_graph.py` | LLM assertion extraction, hypothesis scoring | ~30 min (LLM) |
| 04 | `04_generate_figures.py` | 16 publication-quality PNG figures | ~15 sec |
| 05 | `z_generate_manuscript_variables.py` | `{{VAR}}` → real values plus token manifest | ~2 sec |
| 06 | `06_fulltext_assessment.py` | Open access / PDF availability report | ~5 sec |
| 07 | `07_run_validation_study.py` | Rule-based reference-annotator agreement study — deterministic reproducibility floor, not human validation | ~5 sec |
| 08 | `08_validate_artifacts.py` | Cross-artifact contract and token/figure/provenance gate | seconds |
| 09 | `09_write_pipeline_manifest.py` | Hashes, versions, counts, run IDs, and gate manifest | seconds |
| 10 | `10_release_preflight.py` | Tests, artifact/RDF/metadata/render release gate and local package | seconds/minutes |
| 11 | `11_prepare_evidence_pilots.py` | Deterministic full-text and human-review queues | seconds |
| 12 | `12_snapshot_output.py` | Safe output inventory and non-overwriting snapshot copy | seconds/minutes |

> **Note:** Scripts `01`–`04` and the canonical hydrator must run in order — each stage depends on prior outputs. Scripts `06` and `07` are optional QA steps run independently (07 consumes the `output/data/` corpus + nanopublications produced by `01`/`03`).

## Common Options

Most scripts accept:
- `--log-level {DEBUG,INFO,WARNING,ERROR}` — verbosity control (default: `INFO`) — scripts `01`, `02`, `03`, `04`, `06`
- `--output-dir PATH` — override output directory — scripts `01`, `02`, `03`, `04`, `06`, `07`

Scripts `01` and `03` also accept:
- `--config PATH` — YAML config file for project-specific overrides

**Exceptions:**
- `07_run_validation_study.py` accepts `--output-dir`, `--sample-fraction`, `--min-size`, and `--no-auto-labels` (no `--log-level`).

## Configuration

Settings can be provided via `manuscript/config.yaml`:

```yaml
search:
  query: "active inference free energy principle"
  max_results: 1000
  relevance_keywords:
    - "active inference"
    - "free energy principle"
    - "predictive coding"

knowledge_graph:
  checkpoint_interval: 25
  max_papers: null
```

## Output Structure

All outputs are written to `output/`:
- `output/data/` — JSON/JSONL analysis results, corpus, knowledge graph
- `output/figures/` — Publication-quality PNG figures
- `output/manuscript/` — Rendered markdown with injected variables
- `output/reports/` — `zenodo_deposit_metadata.json` (05), `validation_metrics.json` (07)
- `output/validation/` — `sample.csv`, `labels_rule_reference.csv` (07)

## Dependencies

- **Python 3.12+** with packages listed in `pyproject.toml`
- **Ollama** (optional) — required only for `03_build_knowledge_graph.py` LLM extraction
- **matplotlib** / **networkx** / **scikit-learn** — for analysis and visualization

## Documentation

- **[AGENTS.md](AGENTS.md)** — Detailed technical documentation for each script
- **[../src/](../src/)** — Source modules containing all computational logic
- **[../manuscript/config.yaml](../manuscript/config.yaml)** — Project configuration
