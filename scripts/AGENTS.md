# AGENTS.md — `scripts/` Directory

## Purpose

Project-specific **thin orchestrator scripts** for the Active Inference meta-analysis pipeline. Each script coordinates I/O and sequencing; all computational logic resides in `../src/` modules. Scripts are numbered to indicate execution order.

## Architecture

```
scripts/
├── _bootstrap.py                 # PYTHONPATH + optional infrastructure root
├── _io.py                        # Shared JSON load/write helpers
├── 01_literature_search.py       # → literature/search_runner.py
├── 02_meta_analysis_pipeline.py  # → analysis/pipeline_runner.py
├── 03_build_knowledge_graph.py   # → knowledge_graph/kg_runner.py
├── 04_generate_figures.py        # → visualization/figure_runner.py
├── z_generate_manuscript_variables.py # canonical → manuscript/variables.py
├── 05_inject_variables.py        # compatibility wrapper
├── 06_fulltext_assessment.py     # → literature/fulltext_assessment.py   (auxiliary QA)
├── 07_run_validation_study.py    # → analysis/validation_{sample,labeling,metrics}.py
├── 08_validate_artifacts.py      # → analysis/artifact_contract.py
├── 09_write_pipeline_manifest.py # → analysis/pipeline_manifest.py
├── 10_release_preflight.py       # → local release package, metadata, render, tests
├── 11_prepare_evidence_pilots.py # → deterministic full-text/human queues
├── 12_snapshot_output.py         # → disposable-output inventory/snapshot
├── 13_verify_tooling_inventory.py # → dated source/license/activity probes
├── 14_verify_release_package.py  # → local deposit-equivalent hash check
└── __pycache__/                  # Python bytecode cache (gitignored)
```

Scripts `01`–`05` form the core content-generation chain. Scripts `06`–`09`
perform full-text QA, deterministic validation, cross-artifact validation, and
manifest closure. Scripts `10`–`14` perform release preflight, review-queue
preparation, safe output snapshotting, tooling-source verification, and local
release-package hash verification.

## Execution Order

Scripts **must** run in numbered order because each stage depends on the outputs of prior stages:

| Script | Inputs | Outputs | Dependencies |
|--------|--------|---------|--------------|
| `01` | API responses | `output/data/corpus.jsonl` | Network / cached corpus |
| `02` | `corpus.jsonl` | `subfield_classification.json`, `temporal_analysis.json`, `tfidf_data.json`, `topics.json`, `citation_network.json`, `citation_graph.gml` | `01` |
| `03` | `corpus.jsonl` | `nanopublications.jsonl`, `nanopublications.trig`, extraction state/coverage, scores and summaries | `01`, Ollama |
| `04` | All `output/data/*.json`, `citation_graph.gml` | `output/figures/*.png`, `figure_registry.json` | `02`, `03` |
| `05` | `output/data/*.json`, `manuscript/*.md` | rendered manuscript, token inventory, and artifact hashes | `02`, `03` |
| `06` | `corpus.jsonl` | `fulltext_assessment.json` | `01` |
| `07` | `output/data/nanopublications.jsonl`, `output/data/corpus.jsonl` | `output/validation/sample.csv`, `output/validation/labels_rule_reference.csv`, `output/reports/validation_metrics.json` | `01`, `03` |
| `08` | All current artifacts | `output/reports/artifact_contract.json` | `01`–`07` |
| `09` | Inputs, outputs, and gate reports | `output/reports/pipeline_manifest.json` | `08` |
| `10` | All artifacts, release metadata, and tooling gate | `output/reports/release_preflight.json` | `01`–`09`, `13` |
| `11` | Corpus and validation sample | deterministic review queues/protocols | `01`, `03`, `07` |
| `12` | Disposable `output/` | `output/reports/snapshot_inventory.json`, optional snapshot copy | current output |
| `13` | Tooling registry and public source URLs | `output/reports/tooling_verification.json` | registry, network |
| `14` | Staged release package | local manifest verification report | `10` |

## Script Details

### `01_literature_search.py`

Multi-source literature search orchestrator.

**APIs queried:** arXiv (default query list in `src/config.py` → `DEFAULT_ARXIV_QUERIES`), Semantic Scholar, OpenAlex. Override via `project_config.search.arxiv_queries` in `manuscript/config.yaml`.

**Key flags:**
- `--resume` / `--no-resume` — load existing `corpus.jsonl` before fetching (default: resume on)
- `--clear-corpus` — delete existing corpus and start fresh
- `--skip-arxiv` / `--skip-s2` / `--skip-openalex` — skip individual sources
- `--max-results N` — cap per-source results (default: 1000)
- `--start-year YYYY` — exclude papers before this year
- `--config PATH` — load search settings from YAML

**Relevance filter:** Requires at least one core keyword in title/abstract. Configurable via `search.relevance_keywords` in YAML config.

**Imports from `src/`:** `literature.corpus.Corpus`, `literature.models.Paper`, `literature.arxiv_client`, `literature.semantic_scholar`, `literature.openalex_client`.

### `02_meta_analysis_pipeline.py`

Runs all quantitative analyses: subfield classification, temporal metrics, TF-IDF/NMF topic modeling, and citation network construction with reference normalization.

**Key flags:**
- `--corpus PATH` — path to corpus JSONL
- `--n-topics N` — NMF topic count (default: 8; config-driven)
- `--max-features N` — TF-IDF vocabulary size (default: 500)
- `--min-year YYYY` — pre-filter (default: 2000)
- `--seed N` — NMF random seed (default: 42)

**Stages:**
1. Subfield classification (keyword-based, config-driven)
2. Per-subfield temporal breakdown
3. Global temporal metrics (CAGR, doubling time, peak year)
4. TF-IDF matrix construction
5. NMF topic decomposition
6. Citation network (reference normalization → graph → metrics → communities)

**Imports from `src/`:** `analysis.text_processing`, `analysis.citation_network`, `analysis.temporal_analysis`, `analysis.subfield_classifier`, `analysis.topic_modeling`.

### `03_build_knowledge_graph.py`

LLM-based assertion extraction and hypothesis scoring via Ollama.

**Incremental by default:** Assertions are appended to `nanopublications.jsonl` at checkpoint intervals. On restart, already-processed papers are skipped automatically.

**Key flags:**
- `--llm-model MODEL` — Ollama model name (default: `gemma3:4b`)
- `--llm-url URL` — Ollama API base URL (default: `http://localhost:11434`)
- `--checkpoint-interval N` — flush every N papers (default: 25; config-driven)
- `--clear-assertions` — discard previous extraction results
- `--max-papers N` — limit LLM processing (default: no limit)
- `--config PATH` — load KG settings from YAML

**Outputs:** Nanopublications (JSONL + RDF/TriG), hypothesis scores, temporal trends, assertion summary.

**Imports from `src/`:** `knowledge_graph.schema`, `knowledge_graph.nanopublication`, `knowledge_graph.extraction`, `knowledge_graph.llm_extraction`, `knowledge_graph.hypothesis`.

### `04_generate_figures.py`

Generates all 16 publication-quality figures from analysis JSON files.

**Figure categories:**
- **Field overview:** `field_summary.png`, `subfield_distribution.png`
- **Temporal:** `growth_curve.png`, `subfield_timeline.png`
- **Citation:** `citation_network.png`, `degree_distribution.png`
- **Hypothesis:** `hypothesis_dashboard.png`, `evidence_timeline.png`
- **Text analytics:** `word_cloud.png`, `topic_term_bars.png`, `pca_embeddings.png`, `term_heatmap.png`, `dendrogram.png`, `cooccurrence_matrix.png`
- **Assertions:** `assertion_breakdown.png`, `assertion_summary.png`

**Key flags:**
- `--dpi N` — output resolution (default: 300)
- `--input-dir PATH` — analysis JSON directory
- `--output-dir PATH` — figure output directory

**Uses:** `infrastructure.documentation.figure_manager.FigureManager` for figure registration, `src/visualization/` modules for all rendering.

### `05_inject_variables.py`

Template variable injection: replaces `{{VAR}}` placeholders in manuscript markdown with computed values from pipeline output.

**Key flags:**
- `--project NAME` — project name (default: `act_inf_metaanalysis`)
- `--dry-run` — show changes without writing

**Process:**
1. Compute variables from `output/data/*.json`
2. Write Zenodo deposit metadata to `output/reports/zenodo_deposit_metadata.json` via `write_zenodo_metadata` (occurs before injection; skipped under `--dry-run`)
3. Inject into each `.md` file → write rendered copies to `output/manuscript/`
4. Copy non-md support files (config, bib, etc.)
5. Verify no unresolved `{{VAR}}` placeholders remain

**Imports from `src/`:** `manuscript.variables.compute_variables`, `manuscript.variables.inject_variables`, `manuscript.variables.write_zenodo_metadata`.

### `06_fulltext_assessment.py`

Reports full-text and open-access availability across the corpus.

**Key flags:**
- `--corpus PATH` — corpus JSONL path

**Reports:** Abstract coverage, OA status, PDF URL availability, PDF domain breakdown, identifier coverage (DOI, arXiv, S2, OpenAlex), full-text format assessment (LaTeX source vs publisher PDF vs none).

**Imports from `src/`:** `literature.corpus.Corpus`.

### `07_run_validation_study.py`

Auxiliary QA orchestrator: stratified sampling plus a **rule-based
reference-annotator agreement** study. This is **not** a human validation — the
reference labels are generated by the deterministic keyword-rule protocols in
`analysis.validation_labeling` (`apply_primary_rule_protocol` /
`apply_secondary_rule_protocol`). The resulting metrics measure agreement
between the LLM extraction pipeline and an independent, reproducible rule-based
reference (a reproducibility floor). To run a real human validation, replace the
auto-labeled reference columns in the sample CSV with human annotations and pass
`--no-auto-labels`.

**Key flags:**
- `--output-dir PATH` — output root (default: `<project>/output`)
- `--sample-fraction FLOAT` — stratified sample fraction (default: `0.10`)
- `--min-size N` — minimum sample size floor (default: `200`)
- `--no-auto-labels` — skip rule-based auto-labeling and use pre-filled human labels instead

**Inputs:** `output/data/nanopublications.jsonl`, `output/data/corpus.jsonl` (produced by `01`/`03`).

**Outputs:**
- `output/validation/sample.csv` — stratified sample
- `output/validation/labels_rule_reference.csv` — rule-generated reference labels (both reference columns are rule-based; no separate human file is written)
- `output/reports/validation_metrics.json` — agreement metrics (also mirrored to `output/data/validation_metrics.json`)

**Imports from `src/`:** `analysis.validation_labeling`, `analysis.validation_metrics`, `analysis.validation_sample`.

## Thin Orchestrator Pattern

**CRITICAL:** These scripts must NOT contain computational logic. They:
- Parse CLI arguments
- Load/save JSON and JSONL files
- Import and call `src/` functions
- Log timing and summary statistics

Violations of this pattern break the architecture and test coverage guarantees.

## Configuration

All scripts support `--log-level {DEBUG,INFO,WARNING,ERROR}` for verbosity control.

Scripts `01`, `02`, and `03` auto-discover or accept `--config PATH` pointing to `manuscript/config.yaml` for project-specific overrides (search queries, relevance keywords, checkpoint intervals, custom hypothesis definitions, etc.).

## Output Directory Structure

```
output/
├── data/
│   ├── corpus.jsonl                  # 01
│   ├── subfield_classification.json  # 02
│   ├── subfield_timeline.json        # 02
│   ├── temporal_analysis.json        # 02
│   ├── tfidf_data.json               # 02
│   ├── topics.json                   # 02
│   ├── citation_network.json         # 02
│   ├── citation_graph.gml            # 02
│   ├── nanopublications.jsonl        # 03
│   ├── nanopublications.trig         # 03
│   ├── hypothesis_scores.json        # 03
│   ├── hypothesis_trends.json        # 03
│   ├── assertion_summary.json        # 03
│   ├── fulltext_assessment.json      # 06
│   └── validation_metrics.json       # 07 (mirror of reports/validation_metrics.json)
├── figures/                          # 04
│   ├── *.png (16 figures)
│   └── figure_registry.json
├── manuscript/                       # 05
│   └── *.md (rendered with variables)
├── reports/
│   ├── zenodo_deposit_metadata.json  # 05
│   └── validation_metrics.json       # 07
└── validation/                       # 07
    ├── sample.csv
    └── labels_rule_reference.csv
```
