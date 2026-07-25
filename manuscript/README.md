# Manuscript Source

*A Living Literature Review Architecture for Active Inference: Scalable Assertion Extraction, Nanopublications, and Citation-Weighted Hypothesis Scoring*

Authors: Daniel Friedman (Active Inference Institute) · Joel Dietz (MIT + CIMC)  
DOI: [Zenodo deposit record](https://doi.org/10.5281/zenodo.19461934) · License: CC-BY-4.0

---

## Section Map

| File | Section | Key Variables Injected | Generating Script |
| --- | --- | --- | --- |
| `00_abstract.md` | Abstract | `{{CORPUS_SIZE}}`, `{{YEAR_START}}`, `{{YEAR_END}}`, `{{CAGR_PCT}}`, `{{CITATION_EDGES}}`, `{{CITATION_RESOLUTION_PCT}}` | Stage 5 |
| `01_introduction.md` | Introduction | — | — |
| `02_methods_overview.md` | Methods overview | `{{CORPUS_SIZE}}` | Stage 5 |
| `02a_methods_retrieval.md` | Stage 1: retrieval | `{{CORPUS_SIZE}}`, `{{YEAR_START}}`, `{{YEAR_END}}` | Stage 1 + 5 |
| `02b_methods_extraction.md` | Stage 2: LLM extraction | `{{TOTAL_ASSERTIONS}}` | Stage 3 + 5 |
| `02c_methods_bibliometrics.md` | Stage 2: bibliometrics | `{{NUM_TOPICS}}`, `{{NUM_VOCAB_FEATURES}}` | Stage 2 + 5 |
| `02d_methods_knowledge_graph.md` | Stage 3: knowledge graph | `{{TOTAL_ASSERTIONS}}`, `{{CITATION_RESOLUTION_PCT}}` | Stage 3 + 5 |
| `02e_methods_viz_injection.md` | Stages 4–5 | `{{NUM_FIGURES}}` | Stage 4 + 5 |
| `03_results_hypothesis.md` | Hypothesis results | `{{H1_SCORE}}`…`{{H8_SCORE}}`, support/neutral/contradict counts | Stage 3 + 5 |
| `03a_results_field_overview.md` | Field overview | `{{A1_COUNT}}`, `{{A1_PCT}}`…`{{C5_COUNT}}`, `{{C5_PCT}}`, `{{CAGR_PCT}}`, `{{PEAK_YEAR}}` | Stage 2 + 5 |
| `03b_results_subfields.md` | Subfield analysis | Domain counts per A1/A2/B/C1–C5 | Stage 2 + 5 |
| `03c_results_text_analytics.md` | Text analytics | `{{NUM_TOPICS}}`, `{{NUM_VOCAB_FEATURES}}` | Stage 2 + 5 |
| `03d_results_citation_network.md` | Citation network | `{{CITATION_NODES}}`, `{{CITATION_EDGES}}`, `{{CITATION_DENSITY_PCT}}` | Stage 2 + 5 |
| `04_conclusion.md` | Conclusion | `{{CORPUS_SIZE}}`, `{{TOTAL_ASSERTIONS}}` | Stage 5 |
| `04a_discussion.md` | Discussion | — | — |
| `05_appendix_tooling.md` | Tooling appendix | — | — |
| `06_appendix_technical.md` | Technical appendix | — | — |
| `07_appendix_accessibility.md` | Accessibility appendix | — | — |
| `98_symbols_glossary.md` | Notation + glossary | — | — |
| `99_references.md` | Bibliography | — | — |

---

## Running Stage 5 (Variable Hydration)

```bash
# From project root
python scripts/z_generate_manuscript_variables.py --project .

# Dry run — shows which variables would be injected without writing files
python scripts/z_generate_manuscript_variables.py --project . --dry-run
```

Output goes to `output/manuscript/`. Source files in `manuscript/` are never overwritten. The canonical hydrator also records `output/data/manuscript_variables.json` with the exact source-token inventory and artifact hashes. `scripts/05_inject_variables.py` remains a compatible wrapper.

---

## Adding New Citations

1. Add a BibTeX entry to `references.bib`
2. Use `\citep{key}` or `\citet{key}` in the relevant `.md` section
3. The build system resolves citations via the `references.bib` file during PDF rendering

---

## Configuration

All paper metadata, hypothesis definitions, subfield keywords, and pipeline parameters live in `config.yaml`. Editing `config.yaml` is the primary way to customize the pipeline without touching Python source code.

Key sections:
- `paper` — title, version
- `authors` — name, ORCID, affiliation
- `publication` — DOI, journal, year, license
- `hypothesis_definitions` — H1–H8 definitions (controls LLM extraction)
- `subfield_keywords` — A1–C5 keyword lists (controls domain classification)
- `project_config.search` — arXiv queries, max results, resume behavior
- `project_config.knowledge_graph` — checkpointing, LLM model, temperature
