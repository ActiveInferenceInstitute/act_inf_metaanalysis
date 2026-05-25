# Active Inference Meta-Analysis

**Archived project** under [`projects_archive/act_inf_metaanalysis/`](../../projects_archive/act_inf_metaanalysis/). It is **not** discovered by template pipeline discovery (`projects/` only). To run locally, execute scripts from this directory or promote the tree back to `projects/`.

## Overview

A computational meta-analysis of the Active Inference and Free Energy Principle literature. The project retrieves papers from three academic databases, extracts structured assertions using a nanopublication framework, constructs a probabilistic knowledge graph, scores eight standard hypotheses with citation-weighted evidence, and generates publication-ready visualizations. The pipeline is covered by a pytest suite with a **90% minimum** line-coverage gate in `pyproject.toml`, following the template's thin orchestrator and test-driven development patterns.

## Key Features & Capabilities

### Literature Mining & Retrieval

- **Multi-Source Search**: arXiv Atom API, Semantic Scholar Graph API, OpenAlex API with injectable base URLs for testing
- **Cross-Source Deduplication**: Canonical ID priority scheme (DOI > arXiv ID > S2 ID > OpenAlex ID > title hash)
- **Corpus Management**: JSONL persistence, filtering, merge operations via the `Corpus` class
- **Rate-Limit Aware**: Synchronous clients with configurable delays matching API policies

### Bibliometric Analysis

- **Domain Classification**: Keyword-based mapping to 8 Active Inference domains — A1 formal, A2 philosophy, B tools, C1 neuroscience, C2 robotics, C3 language, C4 psychiatry, C5 biology
- **Temporal Metrics**: Annual publication counts, cumulative growth, CAGR, doubling time estimation
- **Text Analysis**: TF-IDF matrix construction, NMF topic modeling with configurable topic count
- **Citation Network**: networkx DiGraph with PageRank, community detection, and network density metrics

### Knowledge Graph & Hypothesis Scoring

- **RDF Schema**: Custom namespace `http://activeinference.institute/ontology/` with 5 core triple patterns
- **Nanopublications**: Structured assertions with provenance metadata (Assertion + Nanopublication dataclasses)
- **8 Standard Hypotheses**: FEP universality, AIF optimality, Markov blanket realism, predictive coding, scalability, clinical utility, morphogenesis, language as active inference
- **Scoring Formula**: Citation-weighted evidence score in [-1, 1] with log-dampened citation weights and bootstrap 95% CI
- **Temporal Trends**: Cumulative score evaluation at each year for trajectory analysis
- **Graceful Fallback**: rdflib for full RDF support, networkx fallback when rdflib unavailable

### Publication-Ready Visualization

- **16 Figure Types**: Field summary, subfield distribution, growth curve, subfield timeline, citation network, degree distribution, hypothesis dashboard, evidence timeline, word cloud, PCA embeddings, term heatmap, dendrogram, topic-term bars, co-occurrence matrix, assertion type breakdown, assertion summary
- **Colorblind-Safe Palette**: Defined in `VIZ_CONFIG` for accessibility
- **Manuscript Integration**: Figures referenced via LaTeX `\label`/`\ref` in manuscript sections

### Infrastructure Integration

- **Thin Orchestrators**: 6 scripts that import from `src/` for all computation
- **≥90% Test Coverage** (gate in `pyproject.toml`): extensive pytest suite using real data and pytest-httpserver for API testing
- **Deterministic Results**: Fixed RNG seeds (seed=42) for reproducibility
- **Structured Logging**: All scripts use Python `logging` module with configurable `--log-level`
- **Resumable Downloads**: `--resume` flag loads existing corpus before fetching, skipping papers already downloaded
- **Standalone / archived**: Not discovered by template `./run.sh` while under `projects_archive/`; run scripts directly or promote to `projects/` for pipeline integration

## Directory Structure

```text
projects_archive/act_inf_metaanalysis/
├── src/                        # Core library (45+ public APIs, 5 packages)
│   ├── __init__.py
│   ├── literature/             # Multi-source retrieval and corpus management
│   │   ├── __init__.py
│   │   ├── models.py           # Paper, Author, Citation dataclasses
│   │   ├── arxiv_client.py     # arXiv Atom API search + parsing
│   │   ├── semantic_scholar.py # Semantic Scholar Graph API client
│   │   ├── openalex_client.py  # OpenAlex API client
│   │   ├── corpus.py           # Unified corpus: dedup, merge, persist
│   │   ├── search_runner.py    # Stage-01 orchestration
│   │   └── fulltext_assessment.py
│   ├── config_loader.py        # YAML project_config (search, kg)
│   ├── analysis/               # Bibliometric and text analysis
│   │   ├── pipeline_runner.py  # Stage-02 orchestration (imported by script 02)
│   │   ├── text_processing.py  # Tokenization, stopwords, TF-IDF matrix
│   │   ├── citation_network.py # networkx DiGraph, PageRank, communities
│   │   ├── topic_modeling.py   # NMF topic extraction from TF-IDF
│   │   ├── temporal_analysis.py# Publication trends, growth rates, subfield timeline
│   │   ├── subfield_defaults.py# Default keyword map (8 domains)
│   │   ├── subfield_registry.py# Config load + compiled pattern cache
│   │   └── subfield_classifier.py # classify_paper / classify_corpus API
│   ├── knowledge_graph/        # RDF knowledge graph and hypothesis scoring
│   │   ├── kg_runner.py        # Stage-03 orchestration
│   │   ├── llm_config.py       # LLMConfig dataclass
│   │   ├── llm_client.py       # Ollama HTTP client
│   │   ├── llm_prompts.py      # Prompt templates + JSON recovery
│   │   ├── llm_extraction.py   # Batch assess + nanopub persistence
│   │   ├── schema.py           # RDF namespaces, assertion types
│   │   ├── nanopublication.py  # Assertion + Nanopub dataclasses
│   │   ├── hypothesis.py       # 8 hypotheses, citation-weighted scoring
│   │   ├── graph_builder.py    # KnowledgeGraph (rdflib + networkx fallback)
│   │   ├── query.py            # Graph query helpers
│   │   └── extraction.py       # Assertion extraction dispatcher
│   └── visualization/          # Publication-ready figures
│       ├── figure_runner.py    # Stage-04 orchestration
│       ├── advanced/           # Word cloud, PCA, heatmap, dendrogram, topics
│       └── advanced_plots.py   # Re-export shim
├── tests/                      # Pytest suite (see `pyproject.toml` coverage gate)
│   ├── __init__.py
│   ├── conftest.py             # Path setup, MPLBACKEND=Agg, shared fixtures
│   ├── analysis/
│   │   ├── test_citation_network.py
│   │   ├── test_subfield_classifier.py
│   │   ├── test_temporal_analysis.py
│   │   ├── test_text_processing.py
│   │   └── test_topic_modeling.py
│   ├── knowledge_graph/
│   │   ├── llm_extraction_fixtures.py
│   │   ├── test_llm_prompt_parse.py
│   │   ├── test_llm_assess_paper.py
│   │   ├── test_llm_batch.py
│   │   ├── test_llm_config.py
│   │   ├── test_llm_nanopub_resume.py
│   │   ├── test_llm_max_papers.py
│   │   ├── test_extraction.py
│   │   ├── test_graph_builder.py
│   │   ├── test_hypothesis.py
│   │   ├── test_nanopublication.py
│   │   ├── test_query.py
│   │   └── test_schema.py
│   ├── literature/
│   │   ├── test_arxiv_client.py
│   │   ├── test_corpus.py
│   │   ├── test_models.py
│   │   ├── test_openalex_client.py
│   │   └── test_semantic_scholar.py
│   ├── visualization/
│   │   ├── test_advanced_plots.py
│   │   ├── test_citation_plots.py
│   │   ├── test_field_overview.py
│   │   ├── test_hypothesis_charts.py
│   │   ├── test_style.py
│   │   └── test_temporal_plots.py
│   ├── test_scripts.py         # Integration tests for script entry points
│   └── test_variables.py       # Manuscript variable computation tests
├── scripts/                    # Thin orchestrators (≤91 lines each)
│   ├── _bootstrap.py
│   ├── _io.py
│   ├── 01_literature_search.py
│   ├── 02_meta_analysis_pipeline.py
│   ├── 03_build_knowledge_graph.py
│   ├── 04_generate_figures.py
│   ├── 05_inject_variables.py
│   └── 06_fulltext_assessment.py
├── manuscript/                 # 20 sections + references
│   ├── config.yaml
│   ├── preamble.md
│   ├── 00_abstract.md
│   ├── 01_introduction.md
│   ├── 02_methods_overview.md
│   ├── 02a_methods_retrieval.md
│   ├── 02b_methods_extraction.md
│   ├── 02c_methods_bibliometrics.md
│   ├── 02d_methods_knowledge_graph.md
│   ├── 02e_methods_viz_injection.md
│   ├── 03_results_hypothesis.md
│   ├── 03a_results_field_overview.md
│   ├── 03b_results_subfields.md
│   ├── 03c_results_text_analytics.md
│   ├── 03d_results_citation_network.md
│   ├── 04_conclusion.md
│   ├── 04a_discussion.md
│   ├── 05_appendix_tooling.md
│   ├── 06_appendix_technical.md
│   ├── 98_symbols_glossary.md
│   ├── 99_references.md
│   └── references.bib
├── doc/                        # Documentation
│   ├── README.md
│   ├── architecture.md
│   ├── api_reference.md
│   ├── hypotheses.md
│   ├── data_formats.md
│   ├── scripts.md
│   ├── testing.md
│   ├── visualization_guide.md
│   └── CODE_QUALITY_AUDIT.md
├── output/                     # Disposable, regenerated
├── pyproject.toml
├── README.md
└── AGENTS.md
```

## See Also

- [Root AGENTS.md](../../AGENTS.md) --- Template documentation
- [doc/](doc/) --- Architecture, API reference, and hypothesis documentation

*Note: Every directory and subdirectory within `src/` and `tests/` contains localized `AGENTS.md` and `README.md` pairs mapping immediate context.*
