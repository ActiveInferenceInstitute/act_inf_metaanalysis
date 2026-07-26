# Source Code (`src/`)

Core library for the Active Inference Meta-Analysis project. All business logic and computation
lives here; `scripts/` are thin orchestrators that import these modules and handle I/O.
45+ Python modules across 5 subpackages (+ `config.py`, `config_loader.py`), 654 passed / 1 skipped / 90.07% coverage in the latest gate, no mocks.

## Subpackages

| Package | Purpose | Key inputs | Key outputs |
|---|---|---|---|
| `literature/` | Multi-source paper retrieval and corpus management | API queries | `corpus.jsonl` |
| `analysis/` | Bibliometric, temporal, and text analytics | `corpus.jsonl` | Analysis JSONs |
| `knowledge_graph/` | LLM extraction, nanopubs, hypothesis scoring | `corpus.jsonl` | `nanopublications.jsonl`, scores |
| `visualization/` | Publication-ready PNG figure generation | Analysis JSONs | 16 PNG figures |
| `manuscript/` | Template variable computation and injection | All output JSONs | `dict[str, str]` of 191 current-snapshot variables |

## Pipeline Stage → Module Mapping

```
Stage 1 (scripts/01_literature_search.py)
  └─ literature.arxiv_client, literature.openalex_client, literature.semantic_scholar
     literature.corpus, literature.models

Stage 2 (scripts/02_meta_analysis_pipeline.py)
  └─ analysis.subfield_classifier, analysis.temporal_analysis
     analysis.text_processing, analysis.topic_modeling, analysis.citation_network

Stage 3 (scripts/03_build_knowledge_graph.py)
  └─ knowledge_graph.llm_extraction, knowledge_graph.nanopublication
     knowledge_graph.hypothesis, knowledge_graph.graph_builder, knowledge_graph.schema

Stage 4 (scripts/04_generate_figures.py)
  └─ visualization.field_overview, visualization.temporal_plots, visualization.citation_plots
     visualization.hypothesis_charts, visualization.advanced_plots, visualization.style

Stage 5 (scripts/z_generate_manuscript_variables.py)
  └─ manuscript.variables
```

## Testing

```bash
# From project root
PYTHONPATH=/path/to/template .venv/bin/python -m pytest tests/ -q
# 654 passed / 1 skipped / 90.07% coverage, no mocks, deterministic
```

See each subpackage's `README.md` and `AGENTS.md` for module-level details.
