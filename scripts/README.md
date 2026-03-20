# Scripts — Active Inference Meta-Analysis Pipeline

Project-specific orchestrator scripts for the Active Inference literature meta-analysis. Each script is a **thin orchestrator** that coordinates I/O and sequencing; all logic lives in `../src/`.

## Quick Start

```bash
# From the project root (projects/act_inf_metaanalysis/)
cd /path/to/template/projects/act_inf_metaanalysis

# 1. Retrieve literature corpus
python scripts/01_literature_search.py --resume

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
```

## Pipeline Overview

| # | Script | Purpose | Duration |
|---|--------|---------|----------|
| 01 | `01_literature_search.py` | Multi-API corpus retrieval (arXiv, S2, OpenAlex) | ~5 min (first run) |
| 02 | `02_meta_analysis_pipeline.py` | TF-IDF, NMF topics, citation network, temporal analysis | ~30 sec |
| 03 | `03_build_knowledge_graph.py` | LLM assertion extraction, hypothesis scoring | ~30 min (LLM) |
| 04 | `04_generate_figures.py` | 16 publication-quality PNG figures | ~15 sec |
| 05 | `05_inject_variables.py` | `{{VAR}}` → real values in manuscript | ~2 sec |
| 06 | `06_fulltext_assessment.py` | Open access / PDF availability report | ~5 sec |

> **Note:** Scripts must run in order — each stage depends on prior outputs.

## Common Options

All scripts accept:
- `--log-level {DEBUG,INFO,WARNING,ERROR}` — verbosity control (default: `INFO`)
- `--output-dir PATH` — override output directory

Scripts `01`, `02`, `03` also accept:
- `--config PATH` — YAML config file for project-specific overrides

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

## Dependencies

- **Python 3.10+** with packages listed in `pyproject.toml`
- **Ollama** (optional) — required only for `03_build_knowledge_graph.py` LLM extraction
- **matplotlib** / **networkx** / **scikit-learn** — for analysis and visualization

## Documentation

- **[AGENTS.md](AGENTS.md)** — Detailed technical documentation for each script
- **[../src/](../src/)** — Source modules containing all computational logic
- **[../manuscript/config.yaml](../manuscript/config.yaml)** — Project configuration
