# Pipeline Scripts Reference

The meta-analysis pipeline is composed of numbered scripts (01–14) plus the canonical `z_generate_manuscript_variables.py` hydration entrypoint. Each is a **thin orchestrator** that handles only I/O and coordination — all computation is imported from `src/` modules (runners under `src/literature/`, `src/analysis/`, `src/knowledge_graph/`, `src/visualization/`).

Run scripts from the archived project root:

```bash
cd projects/archive/_ActiveInference/act_inf_metaanalysis
```

The live configuration in `manuscript/config.yaml` is the single source of
truth for pipeline and prompt versions, the `gemma3:4b` Ollama endpoint,
eight-topic NMF settings, the frozen temporal snapshot date, and the
PDF/HTML-only render policy. The example configuration mirrors these controls
for a new checkout. `analysis.as_of_date` is intentionally explicit: update it
only when starting a new live literature snapshot.

---

## Stage 1 — Literature Search (`01_literature_search.py` → `literature/search_runner.py`)

Queries arXiv, Semantic Scholar, and OpenAlex, then merges results into a deduplicated `corpus.jsonl`.

### CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--query` | `str` | `config` | Search query string (explicit CLI wins over `search.query`; fallback `"active inference free energy principle"`) |
| `--max-results` | `int` | `config` | Maximum results **per source** (explicit CLI wins over `search.max_results`; fallback `1000`) |
| `--output-dir` | `str` | `output/` | Directory for `corpus.jsonl` |
| `--skip-arxiv` | flag | — | Skip arXiv search |
| `--skip-s2` | flag | — | Skip Semantic Scholar search |
| `--skip-openalex` | flag | — | Skip OpenAlex search |
| `--resume` | flag | config | Load existing corpus before searching (merge) |
| `--no-resume` | flag | — | Ignore existing `corpus.jsonl`; start empty |
| `--clear-corpus` | flag | — | Delete existing corpus before searching |
| `--force-search` | flag | off | Query configured sources while resuming; merge fresh results |
| `--log-level` | choice | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |
| `--config` | `str` | — | Path to YAML config; fills any flag left unset (`--query`, `--max-results`, `--resume`, `--clear-corpus`). Explicitly-passed CLI flags always win over config. |

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

Without `--config`, the script uses default queries from [`src/config.py`](../src/config.py) (`DEFAULT_ARXIV_QUERIES` — core AIF / FEP / predictive-coding / EFE / variational phrasing).

With `--config manuscript/config.yaml`, `project_config.search.arxiv_queries` replaces that list — the bundled config currently defines **nine** queries, adding EBM-, Helmholtz-, Boltzmann-, and contrastive-divergence–adjacent search strings for broader coverage.

Results are merged and deduplicated via `Corpus.add()` (highest `metadata_completeness` wins).

### Semantic Scholar transport policy

Semantic Scholar retrieval uses `/paper/search/bulk`, with continuation tokens and
up to 1,000 records per request. The requested result limit is enforced locally
because the provider can return more records than the requested page size. Bulk
search intentionally omits nested references; detail and citation endpoints are
the only sources for those relationships. The client sends `x-api-key` from the
configured `api_key_env` when available, retries transient 429/5xx and transport
failures three times with bounded `Retry-After`-aware backoff, and records a
terminal 429 as a failed source with rate-limit metadata. A 429 must never be
interpreted as an empty successful result.

### Outputs

| File | Format | Description |
| --- | --- | --- |
| `corpus.jsonl` | JSON Lines | One JSON object per paper (12 fields per record) |
| `reports/search_provenance.json` | JSON | Per-source status, counts, timestamps, and failures |

### Idempotent refresh and resume

For a new snapshot, first preserve the current output tree with a dated,
non-overwriting snapshot, then run the
stages in order. Retrieval is the only stage that intentionally replaces the
corpus; extraction checkpoints are resumable and retain one run ID.

```bash
uv run python scripts/01_literature_search.py --config manuscript/config.yaml \
  --no-resume --clear-corpus
uv run python scripts/02_meta_analysis_pipeline.py --log-level INFO
uv run python scripts/03_build_knowledge_graph.py --config manuscript/config.yaml \
  --clear-assertions --checkpoint-interval 25
uv run python scripts/04_generate_figures.py --dpi 300
uv run python scripts/z_generate_manuscript_variables.py --project .
uv run python scripts/06_fulltext_assessment.py --output-dir output/data
uv run python scripts/07_run_validation_study.py --output-dir output
uv run python scripts/08_validate_artifacts.py
uv run python scripts/09_write_pipeline_manifest.py \
  --render-status pass --validation-status pass
uv run python scripts/11_prepare_evidence_pilots.py
uv run python scripts/12_snapshot_output.py
uv run python scripts/13_verify_tooling_inventory.py
uv run python scripts/10_release_preflight.py
uv run python scripts/14_verify_release_package.py
```

If Ollama or a source is interrupted, rerun the same command without the
clear flag. The extractor skips papers already recorded in its atomic JSONL
checkpoint, while the analysis and figure stages deterministically overwrite
their derived artifacts. The final manifest records input/output hashes,
versions, model, run ID, counts, timestamps, and gate results. A source rate
limit remains a visible gate failure; it must not be hidden by reducing the
requested source scope.

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
| `--n-topics` | `int` | `config` (`8`) | Number of NMF topics to extract; explicit CLI wins over `analysis.n_topics` |
| `--max-features` | `int` | `config` (`500`) | Maximum TF-IDF vocabulary size |
| `--min-year` | `int` | `config` (`2000`) | Filter out papers published before this year |
| `--seed` | `int` | `config` (`42`) | Random seed for NMF reproducibility |
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
| `--llm-url` | `str` | config | Ollama API base URL (the live config uses local port 11435) |
| `--checkpoint-interval` | `int` | `25` | Flush to disk every N papers |
| `--clear-assertions` | flag | — | Delete existing nanopubs and start fresh |
| `--max-papers` | `int` | — | Limit papers to process (useful for testing) |
| `--config` | `str` | — | YAML config path (auto-discovers `manuscript/config.yaml`) |
| `--log-level` | choice | `INFO` | `DEBUG` / `INFO` / `WARNING` / `ERROR` |

### YAML Config Keys (`knowledge_graph` section)

```yaml
knowledge_graph:
  checkpoint_interval: 25
  clear_assertions: false
  max_papers: 100
```

### Incremental Resume

Assertions are persisted to `nanopublications.jsonl` at each checkpoint interval. On restart:

1. The file is read to determine which papers have already been processed
2. Those papers are skipped
3. New results are merged (deduplicating by `(paper_id, hypothesis_id)` — new wins)
4. No separate checkpoint file is needed

### Interrupted-Run Resume

The extractor writes `output/data/extraction_state.json` atomically at start,
each checkpoint, and completion. An interrupted run leaves its JSONL checkpoint
and a non-`complete` state. Resume it with the same configuration and **without**
`--clear-assertions`:

```bash
OLLAMA_NUM_PARALLEL=2 OLLAMA_MAX_LOADED_MODELS=1 \
OLLAMA_CONTEXT_LENGTH=4096 OLLAMA_HOST=127.0.0.1:11435 \
ollama serve

# In a second terminal, from the project root:
python scripts/03_build_knowledge_graph.py \
  --config manuscript/config.yaml \
  --checkpoint-interval 25 \
  --log-level INFO
```

The extractor skips processed paper IDs, preserves the checkpoint's single
`run_id`, and refuses to mix model, prompt, or pipeline versions. The run is
publication-eligible only after `extraction_state.json` reports `complete` and
`extraction_coverage.json` reports zero failed and unprocessed eligible papers.
Use `--clear-assertions` only to intentionally start a new clean extraction run.

### Outputs

| File | Format | Description |
| --- | --- | --- |
| `nanopublications.jsonl` | JSON Lines | Nanopublications with assertions, provenance, timestamps |
| `hypothesis_scores.json` | JSON | Citation-weighted scores for all 8 hypotheses (range `[-1, 1]`) |
| `hypothesis_trends.json` | JSON | Per-hypothesis cumulative score by year |
| `extraction_coverage.json` | JSON | Eligible, processed, failed, and unprocessed paper coverage |
| `extraction_state.json` | JSON | Atomic running/checkpoint/interrupted/complete resume state |
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

## Stage 5 — Manuscript Variable Hydration (`z_generate_manuscript_variables.py`)

Reads pipeline output data, computes template variables, and injects them into manuscript markdown files. Produces rendered copies in `output/manuscript/` with all `{{VAR}}` placeholders replaced by real values. This is the canonical template-recognized hydrator.

### CLI Flags

| Flag | Type | Default | Description |
| --- | --- | --- | --- |
| `--project` | `str` | project root | Project root or project name |
| `--dry-run` | flag | — | Show what would change without writing files |

### Processing Steps

1. **Compute Variables** — Read pipeline output JSONs (`temporal_analysis.json`, `citation_network.json`, `subfield_classification.json`, `assertion_summary.json`, `hypothesis_scores.json`, `topics.json`) and compute the configuration-dependent manuscript variable set (196 variables in the current snapshot) with LaTeX-formatted values
2. **Create Output Directory** — `output/manuscript/` for rendered copies
3. **Inject Variables** — Replace `{{VAR_NAME}}` placeholders in each manuscript `.md` file
4. **Copy Non-MD Files** — Copy `config.yaml`, `references.bib`, etc. to output directory
5. **Verify** — Check for unresolved `{{VAR}}` placeholders in rendered files

### Key Variables

| Variable | Source | Example Value |
| --- | --- | --- |
| `CORPUS_SIZE` | `corpus.jsonl` line count (post-2000) | from latest run |
| `CORPUS_SIZE_LATEX` | Same, LaTeX-formatted | from latest run |
| `INCLUSION_YEAR_START` | `config.yaml` search.start_year | `2000` |
| `INCLUSION_PERIOD` | `{INCLUSION_YEAR_START}–{YEAR_END}` | e.g. `2000–2026` |
| `YEAR_START`, `YEAR_END` | `temporal_analysis.json` empirical span | from latest run |
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

The hydrator also writes `output/data/manuscript_variables.json`, including the exact source-token inventory, source hashes, and artifact manifest used for hydration.

### Example

```bash
# Standard run (canonical entrypoint)
python scripts/z_generate_manuscript_variables.py --project .

# Preview changes without writing
python scripts/z_generate_manuscript_variables.py --project . --dry-run
```

---

## Stage 6 — Full-Text Availability Assessment (`06_fulltext_assessment.py`)

Audits the corpus for full-text availability and produces a JSON report
covering PDF URLs, open-access flags, and per-source breakdowns. This stage
is read-only: it does not modify the corpus, but feeds the manuscript's
methodology and discussion sections about full-text coverage.

**Inputs:**
- `output/data/corpus.jsonl` (Stage 1 product)

**Outputs:**
- Console summary (totals, OA fraction, PDF coverage, source distribution)
- `output/data/fulltext_assessment.json`

**CLI flags:**

| Flag | Default | Description |
| --- | --- | --- |
| `--corpus` | `output/data/corpus.jsonl` | Path to the corpus JSONL file |
| `--output-dir` | `output/data` | Directory to write the assessment JSON |
| `--log-level` | `INFO` | Logging verbosity (`DEBUG`/`INFO`/`WARNING`/`ERROR`) |

**Usage:**

```bash
# Default — uses canonical corpus path
python scripts/06_fulltext_assessment.py

# Custom corpus + output directory
python scripts/06_fulltext_assessment.py \
  --corpus output/data/corpus.jsonl \
  --output-dir output/data
```

The emitted `fulltext_assessment.json` contains keys such as `total_papers`,
`papers_with_pdf_url`, `open_access_count`, and `source_breakdown` (a
`Counter` of `full_text_source` labels). It is consumed by the manuscript
variable injector (Stage 5) and by the appendix sections that report on
data accessibility.

---

## Stage 7 — Deterministic Validation Study (`07_run_validation_study.py`)

Runs the rule-based reference annotator against a deterministic sample and writes
agreement and coverage metrics to `output/data/validation_metrics.json` and
`output/reports/validation_metrics.json`.

## Stage 8 — Cross-Artifact Validation (`08_validate_artifacts.py`)

Checks corpus, subfield, temporal, citation, assertion, hypothesis, provenance,
topic, figure-registry, and manuscript-variable consistency. The command exits
non-zero on any mismatch and writes `output/reports/artifact_contract.json`.

## Stage 9 — Pipeline Manifest (`09_write_pipeline_manifest.py`)

Writes `output/reports/pipeline_manifest.json` with input/output hashes, canonical
pipeline/prompt/model/run identifiers, configured analysis and render policy,
timestamps, counts, and the current render and
validation gate results.

## Stage 10 — Release Preflight (`10_release_preflight.py`)

Runs the test/coverage gate, cross-artifact contract, RDF/TriG parity check,
release metadata checks, dated tooling verification, and PDF/HTML presence
checks without invoking the LLM. Tooling verification is fail-closed: paper-only
sources or repositories without independently verified license/activity metadata
remain visible as blockers.
It writes `output/reports/release_preflight.json` and stages a local,
source-complete-independent nanopublication package under
`output/release/nanopublications-<as_of_date>/`. A failed configured-source gate
keeps the preflight failed even when the local RDF package is valid. Because
Stages 11–13 can add outputs after the initial Stage 09 manifest, Stage 10
refreshes `pipeline_manifest.json` after writing its own report; this is the
final output-hash closure for the documented sequence.

```bash
python scripts/10_release_preflight.py
python scripts/10_release_preflight.py --skip-tests
```

## Stage 11 — Evidence Pilot Preparation (`11_prepare_evidence_pilots.py`)

Writes deterministic, blank review queues and protocols for the bounded
full-text pilot and human calibration. It never invents human labels and never
changes the primary abstract-only analysis.

```bash
python scripts/11_prepare_evidence_pilots.py --fulltext-size 100 --human-size 200
```

## Utility 12 — Snapshot Inventory (`12_snapshot_output.py`)

Writes a deterministic file/size inventory and lists retained snapshots. With
`--label`, it copies the current output tree to a new non-overwriting snapshot;
it never deletes or replaces an existing snapshot.

```bash
python scripts/12_snapshot_output.py
python scripts/12_snapshot_output.py --label 20260725T000000Z
```

## Stage 13 — Tooling Source Verification (`13_verify_tooling_inventory.py`)

Probes the official source pointer for every retained tooling row and records
reachability, repository license metadata, release tags, and recent activity.
Paper-only or incomplete rows remain flagged; this stage never infers a license
or maintenance status.

```bash
python scripts/13_verify_tooling_inventory.py
```

## Stage 14 — Release Package Verification (`14_verify_release_package.py`)

Verifies the staged JSONL/TriG package against its recorded hashes and count.
It also refreshes the pipeline manifest after writing the verification report,
leaving the final manifest as the hash-closed record of the release tree.

Checks every staged nanopublication package file against its recorded SHA-256
and byte count, and verifies the JSONL nanopublication count. This is the local
deposit-equivalent gate; it does not claim that an external deposit exists.

```bash
python scripts/14_verify_release_package.py
```

---

## Full Pipeline

The final release order is dependency-driven: Stages 11–13 run before Stage 10
so the preflight sees the current tooling report, and Stage 10 refreshes the
manifest after its own report/package writes.

```bash
python scripts/01_literature_search.py --config manuscript/config.yaml
python scripts/02_meta_analysis_pipeline.py --n-topics 8 --seed 42
python scripts/03_build_knowledge_graph.py --config manuscript/config.yaml
python scripts/04_generate_figures.py
python scripts/z_generate_manuscript_variables.py --project .
python scripts/06_fulltext_assessment.py
python scripts/07_run_validation_study.py
python scripts/08_validate_artifacts.py
python scripts/09_write_pipeline_manifest.py
python scripts/11_prepare_evidence_pilots.py
python scripts/12_snapshot_output.py
python scripts/13_verify_tooling_inventory.py
python scripts/10_release_preflight.py
python scripts/14_verify_release_package.py
```

---

## Troubleshooting Guide

| Issue | Root Cause | Solution |
| --- | --- | --- |
| **arXiv 403 Forbidden** | Bypassed the 3-second delay rate limit | Ensure you are not running `01_literature_search.py` in multiple terminals simultaneously. |
| **S2 HTTP 429** | Provider throttling, commonly stricter without an API key | The client retries three times with `Retry-After`-aware backoff, then records a failed source. Configure `SEMANTIC_SCHOLAR_API_KEY` and retry with `--force-search`; do not treat the result as a successful empty search. |
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
