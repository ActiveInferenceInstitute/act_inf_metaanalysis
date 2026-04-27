# Pipeline Scripts Reference

The meta-analysis pipeline is composed of five numbered scripts, each a **thin orchestrator** that handles only I/O and coordination — all computation is imported from `src/` modules.

Run scripts from the project root:

```bash
cd projects/act_inf_metaanalysis
```

---

## Stage 1 — Literature Search (`01_literature_search.py`)

Queries arXiv, Semantic Scholar, and OpenAlex, then merges results into a deduplicated `corpus.jsonl`.

### CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--query` | `str` | `"active inference free energy principle"` | Search query string |
| `--max-results` | `int` | `1000` | Maximum results **per source** |
| `--output-dir` | `str` | `output/` | Directory for `corpus.jsonl` |
| `--skip-arxiv` | flag | — | Skip arXiv search |
| `--skip-s2` | flag | — | Skip Semantic Scholar search |
| `--skip-openalex` | flag | — | Skip OpenAlex search |
| `--resume` | flag | on (default) | Load existing corpus before searching (merge) |
| `--no-resume` | flag | — | Ignore existing `corpus.jsonl`; start empty |
| `--clear-corpus` | flag | — | Delete existing corpus before searching |
| `--log-level` | choice | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `--config` | `str` | — | Path to YAML config (overrides `--query`, `--max-results`, `--resume`, `--clear-corpus`) |

### YAML Config Keys (`search` section)

```yaml
search:
  query: "active inference"
  max_results: 500
  resume: true
  clear_corpus: false
  arxiv_queries:        # Override default arXiv query list
    - 'all:"active inference"'
    - 'all:"free energy principle"'
  relevance_keywords:   # Override default relevance filter keywords
    - "active inference"
    - "free energy principle"
    - "predictive coding"
```

### arXiv multi-query strategy

Without `--config`, the script uses the **five** default queries baked into `01_literature_search.py` (core AIF / FEP / predictive-coding / EFE / variational phrasing).

With `--config manuscript/config.yaml`, `project_config.search.arxiv_queries` replaces that list — the bundled config currently defines **nine** queries, adding EBM-, Helmholtz-, Boltzmann-, and contrastive-divergence–adjacent search strings for broader coverage.

Results are merged and deduplicated via `Corpus.add()` (highest `metadata_completeness` wins).

### Outputs

| File | Format | Description |
| --- | --- | --- |
| `corpus.jsonl` | JSON Lines | One JSON object per paper (12 fields per record) |

### Example

```bash
# Full search with all sources
python scripts/01_literature_search.py --max-results 500

# Resume with config file
python scripts/01_literature_search.py --config manuscript/config.yaml

# arXiv only, fresh start
python scripts/01_literature_search.py --skip-s2 --skip-openalex --clear-corpus
```

---

## Stage 2 — Meta-Analysis Pipeline (`02_meta_analysis_pipeline.py`)

Loads the corpus and runs all analysis modules: domain classification, temporal analysis, TF-IDF text processing, NMF topic modeling, and citation network construction.

### CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--corpus` | `str` | `output/data/corpus.jsonl` | Path to input corpus |
| `--output-dir` | `str` | `output/` | Directory for analysis JSON results |
| `--n-topics` | `int` | `5` | Number of NMF topics to extract |
| `--max-features` | `int` | `500` | Maximum TF-IDF vocabulary size |
| `--min-year` | `int` | `1960` | Filter out papers published before this year |
| `--seed` | `int` | `42` | Random seed for NMF reproducibility |
| `--log-level` | choice | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### Processing Steps

1. **Domain Classification** — Priority-based keyword classification into 8 domains (C→B→A1→A2) with regex word boundaries via `subfield_classifier.classify_corpus()`
2. **Domain Timeline** — Per-domain year-by-year publication counts
3. **Temporal Analysis** — Publication trends, CAGR, doubling time via `temporal_analysis.compute_temporal_metrics()`
4. **TF-IDF Matrix** — Text processing with `build_tfidf_matrix()`, `--max-features` vocabulary size (default 500), L2-normalized rows
5. **NMF Topic Modeling** — Multiplicative-update NMF via `fit_nmf_topics()`
6. **Citation Network** — Reference normalization, graph construction, PageRank, community detection

### Outputs

| File | Format | Description |
| --- | --- | --- |
| `subfield_classification.json` | JSON | Domain → paper count mapping |
| `subfield_timeline.json` | JSON | Domain → {year → count} nested mapping |
| `temporal_analysis.json` | JSON | Year counts, cumulative, CAGR, peak year, doubling time |
| `tfidf_data.json` | JSON | Full TF-IDF matrix, feature names, domain labels, tokenized docs |
| `topics.json` | JSON | NMF topics with top-10 words and weights per topic |
| `citation_network.json` | JSON | Network metrics: nodes, edges, density, PageRank top-5, HITS top-5 |
| `citation_graph.gml` | GML | Full NetworkX directed graph (nodes + edges) |

### Example

```bash
python scripts/02_meta_analysis_pipeline.py --n-topics 8
```

---

## Stage 3 — Knowledge Graph Construction (`03_build_knowledge_graph.py`)

Extracts structured assertions from paper abstracts using an LLM (Ollama), scores hypotheses, and computes temporal trends. **Incremental by default** — already-processed papers are skipped on restart.

### CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--corpus` | `str` | `output/data/corpus.jsonl` | Path to input corpus |
| `--output-dir` | `str` | `output/` | Directory for KG results |
| `--llm-model` | `str` | `gemma3:4b` | Ollama model name |
| `--llm-url` | `str` | `http://localhost:11434` | Ollama API base URL |
| `--checkpoint-interval` | `int` | `50` | Flush to disk every N papers |
| `--clear-assertions` | flag | — | Delete existing nanopubs and start fresh |
| `--max-papers` | `int` | — | Limit papers to process (useful for testing) |
| `--config` | `str` | — | YAML config path (auto-discovers `manuscript/config.yaml`) |
| `--log-level` | choice | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### YAML Config Keys (`knowledge_graph` section)

```yaml
knowledge_graph:
  checkpoint_interval: 50
  clear_assertions: false
  max_papers: 100
```

### Incremental Resume

Assertions are persisted to `nanopublications.jsonl` at each checkpoint interval. On restart:

1. The file is read to determine which papers have already been processed
2. Those papers are skipped
3. New results are merged (deduplicating by `(paper_id, hypothesis_id)` — new wins)
4. No separate checkpoint file is needed

### Outputs

| File | Format | Description |
| --- | --- | --- |
| `nanopublications.jsonl` | JSON Lines | Nanopublications with assertions, provenance, timestamps |
| `hypothesis_scores.json` | JSON | Citation-weighted scores for all 8 hypotheses (range `[-1, 1]`) |
| `hypothesis_trends.json` | JSON | Per-hypothesis cumulative score by year |
| `assertion_summary.json` | JSON | Total assertions, type counts, per-hypothesis breakdown |

### Example

```bash
# Standard run (incremental)
python scripts/03_build_knowledge_graph.py --config manuscript/config.yaml

# Fresh start with limited papers
python scripts/03_build_knowledge_graph.py --clear-assertions --max-papers 50

# Use a different model
python scripts/03_build_knowledge_graph.py --llm-model llama3.2:3b
```

---

## Stage 4 — Figure Generation (`04_generate_figures.py`)

Reads analysis JSON files and generates publication-quality figures. Forces `MPLBACKEND=Agg` for headless rendering.

### CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--input-dir` | `str` | `output/` | Directory containing analysis JSONs |
| `--output-dir` | `str` | `output/figures/` | Directory for generated PNGs |
| `--dpi` | `int` | `300` | Output figure DPI |
| `--log-level` | choice | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### Generated Figures

| Figure | Source Data | Description |
| --- | --- | --- |
| `field_summary.png` | `subfield_classification.json` | Horizontal bar chart of papers per domain |
| `subfield_distribution.png` | `subfield_classification.json` | Pie chart with <2% slice grouping |
| `growth_curve.png` | `temporal_analysis.json` | Dual-axis: annual counts + cumulative growth |
| `subfield_timeline.png` | `subfield_timeline.json` | Stacked area chart of domain trends over time |
| `citation_network.png` | `citation_graph.gml` | Spring-layout network graph |
| `degree_distribution.png` | `citation_graph.gml` | In/out-degree histogram |
| `hypothesis_dashboard.png` | `hypothesis_scores.json` | Diverging bar chart of hypothesis support |
| `evidence_timeline.png` | `hypothesis_trends.json` | Multi-line cumulative evidence trends |
| `word_cloud.png` | `topics.json` | Word cloud from NMF topic top-words |
| `topic_term_bars.png` | `topics.json` | Faceted bars of top terms per topic |
| `pca_embeddings.png` | `tfidf_data.json` | 2-D PCA scatter with loading arrows |
| `term_heatmap.png` | `tfidf_data.json` | Mean TF-IDF by domain × top terms |
| `dendrogram.png` | `tfidf_data.json` | Ward-linkage clustering of domain centroids |
| `cooccurrence_matrix.png` | `tfidf_data.json` | Top-30 term co-occurrence heatmap |
| `assertion_breakdown.png` | `assertion_summary.json` | Per-hypothesis assertion type stacked bars |
| `assertion_summary.png` | `assertion_summary.json` | Panel with total, type counts, and per-hypothesis totals |

### Example

```bash
python scripts/04_generate_figures.py --dpi 600
```

---

## Stage 5 — Manuscript Variable Injection (`05_inject_variables.py`)

Reads pipeline output data, computes template variables, and injects them into manuscript markdown files. Produces rendered copies in `output/manuscript/` with all `{{VAR}}` placeholders replaced by real values.

### CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--project` | `str` | `act_inf_metaanalysis` | Project name |
| `--dry-run` | flag | — | Show what would change without writing files |

### Processing Steps

1. **Compute Variables** — Read pipeline output JSONs (`temporal_analysis.json`, `citation_network.json`, `subfield_classification.json`, `assertion_summary.json`, `hypothesis_scores.json`, `topics.json`) and compute ~50 template variables with LaTeX-formatted values
2. **Create Output Directory** — `output/manuscript/` for rendered copies
3. **Inject Variables** — Replace `{{VAR_NAME}}` placeholders in each manuscript `.md` file
4. **Copy Non-MD Files** — Copy `config.yaml`, `references.bib`, etc. to output directory
5. **Verify** — Check for unresolved `{{VAR}}` placeholders in rendered files

### Key Variables

| Variable | Source | Example Value |
| --- | --- | --- |
| `CORPUS_SIZE` | `corpus.jsonl` line count | `775` |
| `CORPUS_SIZE_LATEX` | Same, LaTeX-formatted | `775` |
| `YEAR_START`, `YEAR_END` | `temporal_analysis.json` | `2010`, `2024` |
| `CAGR_PCT` | `temporal_analysis.json` | `26.00` |
| `CITATION_EDGES` | `citation_network.json` | `1{,}834` |
| `A1_COUNT`, `A1_PCT` | `subfield_classification.json` | `75`, `9.7` |
| `FEP_UNIVERSALITY_SCORE` | `hypothesis_scores.json` | `+0.82` |
| `NUM_FIGURES` | `output/figures/*.png` count | `16` |

### Outputs

| File | Format | Description |
| --- | --- | --- |
| `output/manuscript/*.md` | Markdown | Rendered manuscript files with real values |
| `output/manuscript/config.yaml` | YAML | Copied configuration |
| `output/manuscript/references.bib` | BibTeX | Copied references |

### Example

```bash
# Standard run
python scripts/05_inject_variables.py

# Preview changes without writing
python scripts/05_inject_variables.py --dry-run
```

---

## Full Pipeline

```bash
python scripts/01_literature_search.py --config manuscript/config.yaml
python scripts/02_meta_analysis_pipeline.py
python scripts/03_build_knowledge_graph.py --config manuscript/config.yaml
python scripts/04_generate_figures.py
python scripts/05_inject_variables.py
```

---

## Troubleshooting Guide

| Issue | Root Cause | Solution |
| --- | --- | --- |
| **arXiv 403 Forbidden** | Bypassed the 3-second delay rate limit | Ensure you are not running `01_literature_search.py` in multiple terminals simultaneously. |
| **S2 HTTP 429** | Semantic Scholar hard limits (e.g., 100 requests / 5 minutes) | The script will auto-retry with exponential backoff. Do not kill the script; let it sleep and recover. |
| **Ollama Connection Refused** | Local LLM server is not running | Run `ollama serve` in a background terminal before starting `03_build_knowledge_graph.py`. |
| **JSONDecodeError in Stage 3** | The LLM generated malformed JSON | Decrease `temperature` in config (e.g., `0.05`), or increase `max_retries`. |
| **Empty `output/figures/`** | `matplotlib` lacks the backend | The scripts automatically force `MPLBACKEND=Agg` (headless). If rendering still fails, ensure `pip install matplotlib` completed. |

---

## Steganographic Hardening

While the standard `./run.sh` pipeline produces `output/pdf/{name}_combined.pdf`, the system is also capable of producing a cryptographically hardened, steganographic version of the final manuscript via `secure_run.sh`.

```bash
# Execute the full pipeline, then harden the PDF output
./secure_run.sh --pipeline
```

This enforces diagonal watermark overlays, invisible hash layers, and injects a cryptographic manifest that can be verified to prove the document was not tampered with post-generation. See `infrastructure/steganography/` for the cryptographic backend constraints.

> **Repository:** [github.com/ActiveInferenceInstitute/act_inf_metaanalysis](https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis)
