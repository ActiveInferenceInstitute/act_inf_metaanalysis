# Methodology: Pipeline Design and Formal Definitions \label{sec:methods}

This section describes the five-stage computational meta-analysis pipeline. Each stage corresponds to a tested, independently executable script that reads upstream outputs and produces structured artifacts. The pipeline extends the systematic literature analysis approach of Knight et al. \citep{knight2022fep}—which combined manual annotation with ontology-based automated analysis—by substituting manual coding with fully automated, LLM-driven assertion extraction and citation-weighted hypothesis scoring.

## Pipeline Overview

| Stage | Script | Primary Input | Primary Output | Section |
| --- | --- | --- | --- | --- |
| 1 | `01_literature_search.py` | API queries | `corpus.jsonl` | \hyperref[sec:methods_retrieval]{Retrieval} |
| 2 | `02_meta_analysis_pipeline.py` | `corpus.jsonl` | Classification, temporal, TF-IDF, NMF, citation network JSONs | \hyperref[sec:methods_bibliometrics]{Bibliometrics} |
| 3 | `03_build_knowledge_graph.py` | `corpus.jsonl` | `nanopublications.jsonl`, `nanopublications.trig`, scores | \hyperref[sec:methods_kg]{Knowledge Graph} |
| 4 | `04_generate_figures.py` | All Stage 2–3 JSONs | 16 publication-ready PNGs | \hyperref[sec:methods_viz]{Visualization} |
| 5 | `05_inject_variables.py` | All output JSONs | Rendered manuscript Markdown | \hyperref[sec:methods_viz]{Injection} |

Scripts act as thin orchestrators that import methods from tested library modules and handle file I/O. All computation resides in the `src/` packages; no analysis logic is embedded in scripts.
