# Active Inference Meta-Analysis

**Archived project** under `projects_archive/act_inf_metaanalysis/` in the template monorepo (when checked out there). As a standalone repository it is **not** discovered by template pipeline discovery (`projects/` only). To run locally, execute scripts from this directory or promote the tree back to `projects/`.

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

- **Thin Orchestrators**: 13 numbered scripts (01–04, 06–14) plus the canonical manuscript hydrator import from `src/` for all computation
- **≥90% Test Coverage** (gate in `pyproject.toml`): extensive pytest suite using real data and pytest-httpserver for API testing
- **Deterministic Results**: Fixed RNG seeds (seed=42) for reproducibility
- **Structured Logging**: All scripts use Python `logging` module with configurable `--log-level`
- **Resumable Downloads**: `--resume` flag loads existing corpus before fetching, skipping papers already downloaded
- **Standalone / archived**: Not discovered by template `./run.sh` while under `projects_archive/`; run scripts directly or promote to `projects/` for pipeline integration

## Directory Structure

```text
projects_archive/act_inf_metaanalysis/
├── act_inf_metaanalysis_v2.0.6_2026-07-26.pdf  # date-stamped publication artifact
├── src/                        # Core library (5 packages, 47 modules)
│   ├── __init__.py
│   ├── config.py               # Centralized path/seed/query constants
│   ├── config_loader.py        # YAML project_config (search, kg)
│   ├── literature/             # Multi-source retrieval and corpus management
│   │   ├── models.py           # Paper, Author, Citation dataclasses
│   │   ├── arxiv_client.py     # arXiv Atom API search + parsing
│   │   ├── semantic_scholar.py # Semantic Scholar Graph API client
│   │   ├── openalex_client.py  # OpenAlex API client
│   │   ├── corpus.py           # Unified corpus: dedup, merge, persist
│   │   ├── search_runner.py    # Stage-01 orchestration
│   │   └── fulltext_assessment.py # Stage-06 OA/PDF availability report
│   ├── analysis/               # Bibliometric and text analysis
│   │   ├── pipeline_runner.py  # Stage-02 orchestration (imported by script 02)
│   │   ├── text_processing.py  # Tokenization, stopwords, TF-IDF matrix
│   │   ├── citation_network.py # networkx DiGraph, PageRank, communities
│   │   ├── topic_modeling.py   # NMF topic extraction from TF-IDF
│   │   ├── topic_stability.py  # Alternate-seed topic stability diagnostics
│   │   ├── temporal_analysis.py# Publication trends, growth rates, subfield timeline
│   │   ├── subfield_defaults.py# Default keyword map (8 domains)
│   │   ├── subfield_registry.py# Config load + compiled pattern cache
│   │   ├── subfield_classifier.py # classify_paper / classify_corpus API
│   │   ├── validation_sample.py, validation_labeling.py, validation_metrics.py  # Stage-07 rule-based reference study
│   │   ├── artifact_contract.py# Stage-08 cross-artifact contract
│   │   ├── pipeline_manifest.py# Stage-09 hash/gate manifest
│   │   ├── release_package.py  # Stage-10 local nanopub package
│   │   ├── pilot_protocol.py   # Stage-11 full-text/human review queues
│   │   ├── snapshot_manager.py # Stage-12 atomic snapshot inventory/copy
│   │   └── tooling_verification.py # Stage-13 source/license probes
│   ├── knowledge_graph/        # RDF knowledge graph and hypothesis scoring
│   │   ├── kg_runner.py        # Stage-03 orchestration
│   │   ├── llm_config.py       # LLMConfig dataclass (0.6 confidence floor)
│   │   ├── llm_client.py       # Ollama HTTP client
│   │   ├── llm_prompts.py      # Prompt templates + JSON recovery
│   │   ├── llm_extraction.py   # Batch assess + nanopub persistence
│   │   ├── schema.py           # RDF namespaces, assertion types
│   │   ├── nanopublication.py  # Assertion + Nanopub dataclasses, atomic JSONL
│   │   ├── hypothesis.py       # 8 hypotheses, citation-weighted scoring
│   │   ├── hypothesis_weights.py # Sensitivity weight policies
│   │   ├── sensitivity.py      # Weight-policy sensitivity analysis
│   │   ├── provenance.py       # Structured extraction provenance summary
│   │   ├── graph_builder.py    # KnowledgeGraph (rdflib + networkx fallback)
│   │   ├── query.py            # Graph query helpers
│   │   └── extraction.py       # Assertion extraction dispatcher
│   ├── visualization/          # Publication-ready figures
│   │   ├── figure_runner.py    # Stage-04 orchestration
│   │   ├── style.py            # Wong (2011) palette, 16pt font floor
│   │   ├── field_overview.py, citation_plots.py, temporal_plots.py,
│   │   ├── hypothesis_charts.py, advanced_plots.py (re-export shim)
│   │   └── advanced/           # labels, word_cloud, embeddings, topics
│   └── manuscript/             # Manuscript variable computation
│       └── variables.py        # compute_variables / inject_variables
├── tests/                      # Pytest suite (see `pyproject.toml` coverage gate)
│   ├── conftest.py             # Path setup, MPLBACKEND=Agg, shared fixtures
│   ├── analysis/               # 16 test modules incl. validation, contract, snapshots
│   ├── knowledge_graph/        # 15 test modules incl. LLM resume/config/max-papers
│   ├── literature/             # 8 test modules incl. search_runner + httpserver
│   ├── visualization/          # 7 test modules incl. figure_runner
│   ├── test_scripts.py         # Integration tests for script entry points
│   ├── test_variables.py       # Manuscript variable computation tests
│   ├── test_config_loader.py   # YAML load paths + no-mock ImportError fallback
│   ├── test_quality_remediation.py # W1–W3 regression guards
│   └── test_suite_inventory.py # AST guard: no shadowed/duplicate test classes
├── scripts/                    # Thin orchestrators (I/O + sequencing only; logic in src/)
│   ├── _bootstrap.py
│   ├── _io.py
│   ├── 01_literature_search.py
│   ├── 02_meta_analysis_pipeline.py
│   ├── 03_build_knowledge_graph.py
│   ├── 04_generate_figures.py
│   ├── z_generate_manuscript_variables.py
│   ├── 06_fulltext_assessment.py   # auxiliary QA (full-text availability)
│   ├── 07_run_validation_study.py  # auxiliary QA (rule-based reference-annotator agreement)
│   ├── 08_validate_artifacts.py    # cross-artifact contract
│   ├── 09_write_pipeline_manifest.py
│   ├── 10_release_preflight.py
│   ├── 11_prepare_evidence_pilots.py
│   ├── 12_snapshot_output.py
│   ├── 13_verify_tooling_inventory.py
│   └── 14_verify_release_package.py
├── manuscript/                 # 20 sections + references
│   ├── config.yaml             # Single source of truth (paper, hypotheses, pipeline)
│   ├── config.yaml.example     # Stripped template for new checkouts
│   ├── preamble.md
│   ├── 00_abstract.md … 07_appendix_accessibility.md, 98_symbols_glossary.md,
│   ├── 99_references.md
│   └── references.bib
├── data/validation/            # Rule-based reference-annotator agreement schema
│   └── annotation_schema.md
├── doc/                        # Documentation hub
│   ├── README.md               # Index + onboarding
│   ├── architecture.md, api_reference.md, data_formats.md, hypotheses.md,
│   ├── scripts.md, testing.md, visualization_guide.md,
│   ├── ai_meta_analysis_playbook.md, CODE_QUALITY_AUDIT.md
│   └── tooling_inventory.yaml  # Publication-facing tooling source registry
├── output/                     # Versioned generated publication artifacts
├── .github/workflows/ci.yml    # ruff + mypy + pytest 90% gate
├── pyproject.toml
├── uv.lock
├── LICENSE                     # CC-BY-4.0
├── CHANGELOG.md
├── TODO.md
├── README.md
└── AGENTS.md
```

## See Also

- [README.md](README.md) --- Project overview, quick start, and changelog pointer
- [TODO.md](TODO.md) --- Authoritative forward backlog (Minor / Medium / Major)
- [doc/](doc/) --- Architecture, API reference, and hypothesis documentation
- [LICENSE](LICENSE) --- CC-BY-4.0 license terms

*Note: Every directory and subdirectory within `src/` and `tests/` contains localized `AGENTS.md` and `README.md` pairs mapping immediate context.*
