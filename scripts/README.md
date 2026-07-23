# Scripts — Active Inference Meta-Analysis Pipeline

Project-specific orchestrator scripts for the Active Inference literature meta-analysis. Each script is a **thin orchestrator** that coordinates I/O and sequencing; all logic lives in `../src/`.

## Quick Start

```bash
# From the project root (projects_archive/act_inf_metaanalysis/)
cd /path/to/template/projects_archive/act_inf_metaanalysis

# 1. Retrieve literature corpus (default: merge into existing corpus.jsonl; use --no-resume to ignore it)
python scripts/01_literature_search.py

# 2. Run quantitative analyses
python scripts/02_meta_analysis_pipeline.py

# 3. Build knowledge graph (requires Ollama for LLM extraction)
python scripts/03_build_knowledge_graph.py --llm-model gemma3:4b

# 4. Generate publication figures
python scripts/04_generate_figures.py --dpi 300

# 5. Inject variables into manuscript templates
python scripts/05_inject_variables.py

# 6. Assess full-text availability
python scripts/06_fulltext_assessment.py

# 7. (Validation / QA — optional) Rule-based reference-annotator agreement study
python scripts/07_run_validation_study.py --sample-fraction 0.10 --min-size 200
```

Scripts `01`–`05` are the core content-generation chain (run in order). Scripts `06` and `07` are auxiliary QA tools run independently after `03`/`05`.

## Pipeline Overview

| # | Script | Purpose | Duration |
|---|--------|---------|----------|
| 01 | `01_literature_search.py` | Multi-API corpus retrieval (arXiv, S2, OpenAlex) | ~5 min (first run) |
| 02 | `02_meta_analysis_pipeline.py` | TF-IDF, NMF topics, citation network, temporal analysis | ~30 sec |
| 03 | `03_build_knowledge_graph.py` | LLM assertion extraction, hypothesis scoring | ~30 min (LLM) |
| 04 | `04_generate_figures.py` | 16 publication-quality PNG figures | ~15 sec |
| 05 | `05_inject_variables.py` | `{{VAR}}` → real values in manuscript | ~2 sec |
| 06 | `06_fulltext_assessment.py` | Open access / PDF availability report (auxiliary QA) | ~5 sec |
| 07 | `07_run_validation_study.py` | Rule-based reference-annotator agreement study — deterministic reproducibility floor, not human validation (auxiliary QA) | ~5 sec |

> **Note:** Scripts `01`–`05` must run in order — each stage depends on prior outputs. Scripts `06` and `07` are optional QA steps run independently (07 consumes the `output/data/` corpus + nanopublications produced by `01`/`03`).

## Common Options

Most scripts accept:
- `--log-level {DEBUG,INFO,WARNING,ERROR}` — verbosity control (default: `INFO`) — scripts `01`, `02`, `03`, `04`, `06`
- `--output-dir PATH` — override output directory — scripts `01`, `02`, `03`, `04`, `06`, `07`

Scripts `01`, `02`, `03` also accept:
- `--config PATH` — YAML config file for project-specific overrides

**Exceptions:**
- `05_inject_variables.py` accepts **only** `--project NAME` and `--dry-run` (no `--log-level`, no `--output-dir`; it resolves paths from the project root).
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
  checkpoint_interval: 50
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

- **Python 3.10+** with packages listed in `pyproject.toml`
- **Ollama** (optional) — required only for `03_build_knowledge_graph.py` LLM extraction
- **matplotlib** / **networkx** / **scikit-learn** — for analysis and visualization

## Documentation

- **[AGENTS.md](AGENTS.md)** — Detailed technical documentation for each script
- **[../src/](../src/)** — Source modules containing all computational logic
- **[../manuscript/config.yaml](../manuscript/config.yaml)** — Project configuration
