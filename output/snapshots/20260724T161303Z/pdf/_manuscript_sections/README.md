# Manuscript Source

*A Living Literature Review Architecture for Active Inference: Scalable Assertion Extraction, Nanopublications, and Citation-Weighted Hypothesis Scoring*

Authors: Daniel Friedman (Active Inference Institute) · Joel Dietz (MIT + CIMC)  
DOI: [10.5281/zenodo.19461934](https://doi.org/10.5281/zenodo.19461934) · License: CC-BY-4.0

---

## Section Map

| File | Section | Key Variables Injected | Generating Script |
| --- | --- | --- | --- |
| `00_abstract.md` | Abstract | `817`, `2005`, `2026`, `20.36`, `2,176`, `7.4` | Stage 5 |
| `01_introduction.md` | Introduction | — | — |
| `02_methods_overview.md` | Methods overview | `817` | Stage 5 |
| `02a_methods_retrieval.md` | Stage 1: retrieval | `817`, `2005`, `2026` | Stage 1 + 5 |
| `02b_methods_extraction.md` | Stage 2: LLM extraction | `1,671` | Stage 3 + 5 |
| `02c_methods_bibliometrics.md` | Stage 2: bibliometrics | `8`, `500` | Stage 2 + 5 |
| `02d_methods_knowledge_graph.md` | Stage 3: knowledge graph | `1,671`, `7.4` | Stage 3 + 5 |
| `02e_methods_viz_injection.md` | Stages 4–5 | `16` | Stage 4 + 5 |
| `03_results_hypothesis.md` | Hypothesis results | `+0.13`…`+0.81`, support/neutral/contradict counts | Stage 3 + 5 |
| `03a_results_field_overview.md` | Field overview | `64`, `7.8`…`135`, `16.5`, `20.36`, `2025` | Stage 2 + 5 |
| `03b_results_subfields.md` | Subfield analysis | Domain counts per A1/A2/B/C1–C5 | Stage 2 + 5 |
| `03c_results_text_analytics.md` | Text analytics | `8`, `500` | Stage 2 + 5 |
| `03d_results_citation_network.md` | Citation network | `817`, `2,176`, `0.33` | Stage 2 + 5 |
| `04_conclusion.md` | Conclusion | `817`, `1,671` | Stage 5 |
| `04a_discussion.md` | Discussion | — | — |
| `05_appendix_tooling.md` | Tooling appendix | — | — |
| `06_appendix_technical.md` | Technical appendix | — | — |
| `07_appendix_accessibility.md` | Accessibility appendix | — | — |
| `98_symbols_glossary.md` | Notation + glossary | — | — |
| `99_references.md` | Bibliography | — | — |

---

## Running Stage 5 (Variable Injection)

```bash
# From project root
PYTHONPATH=/path/to/template python scripts/05_inject_variables.py

# Dry run — shows which variables would be injected without writing files
PYTHONPATH=/path/to/template python scripts/05_inject_variables.py --dry-run
```

Output goes to `output/manuscript/`. Source files in `manuscript/` are never overwritten.

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
