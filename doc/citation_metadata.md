# Citation Metadata

How citation metadata enters the pipeline, where it is stored, and how to cite this
snapshot. This page covers the bibliographic and citation layer only; field-level
schemas for the generated artifacts live in [`data_formats.md`](data_formats.md), and
the stage that builds the citation network is described in
[`architecture.md`](architecture.md) and [`scripts.md`](scripts.md).

## 1. Citing this work

The machine-readable citation record is [`CITATION.cff`](../CITATION.cff) at the
repository root (Citation File Format 1.2.0). It is the single source of truth for
the release citation:

| Field | Value |
| --- | --- |
| Title | `act_inf_metaanalysis: A computational meta-analysis of the Active Inference literature` |
| Version | `2.0.6` |
| Date released | `2026-07-26` |
| DOI | `10.5281/zenodo.19461934` |
| License | `CC-BY-4.0` |
| Authors | Daniel Friedman (Active Inference Institute), Joel Dietz (MIT) |
| URL | <https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis> |

Cite the software/data snapshot through the DOI above. The date-stamped root PDF
[`act_inf_metaanalysis_v2.0.6_2026-07-26.pdf`](../act_inf_metaanalysis_v2.0.6_2026-07-26.pdf)
is the public release copy; `output/pdf/act_inf_metaanalysis_combined.pdf` is the
reproducible pipeline render.

## 2. Per-paper citation metadata in the corpus

Every retrieved work is a [`src/literature/models.py`](../src/literature/models.py)
`Paper` record persisted one-per-line in `output/data/corpus.jsonl`. The
citation-relevant fields are:

| Field | Meaning |
| --- | --- |
| `doi` | Digital Object Identifier, when the source exposes one |
| `arxiv_id` | arXiv identifier (e.g. `2301.12345`) |
| `s2_id` | Semantic Scholar paper ID |
| `openalex_id` | OpenAlex work ID |
| `citation_count` | Cited-by count used for weighting (never negative; `null` → `0`) |
| `references` | Canonical IDs this paper cites (outbound edges) |
| `venue` | Publication venue or journal |
| `year`, `publication_date` | Bibliographic date fields |

`Paper.canonical_id` resolves a single stable identity with the priority
**`doi > arxiv_id > s2_id > openalex_id > title hash`**. The title fallback is
`sha256(title.lower().strip())[:16]` (deterministic across runs). This priority is
also the cross-source deduplication key: `Corpus.add()` keeps the record with the
higher `metadata_completeness`, so the richest citation metadata wins. See
[`data_formats.md`](data_formats.md) for the exact JSONL schema and
[`api_reference.md`](api_reference.md) for the model API.

The retrieval clients and their rate limits are documented in the source-module
guides (`src/literature/AGENTS.md`); the Semantic Scholar bulk probe is the
network-dependent step that gates a fresh live refresh.

## 3. Citation metadata in the knowledge graph

Extracted assertions carry a citation-weighted evidence score. The weight is
`log(1 + citation_count)` (log-damped so hyper-cited foundational papers do not
dominate), and each `Assertion` records the `citation_count` it used so the score is
reproducible. The scoring formula and sensitivity policies live in
[`hypotheses.md`](hypotheses.md) and `src/knowledge_graph/hypothesis_weights.py`.

Reference provenance for the manuscript is carried by the docstrings and the
per-nanopublication provenance fields, not by a separate citation registry.

## 4. Citation-network artifacts

Stage 2 (`02_meta_analysis_pipeline.py`) builds the citation graph from the
`references` edges in the corpus and writes:

| Artifact | Format | Contents |
| --- | --- | --- |
| `output/data/citation_network.json` | JSON | Node/edge counts, density, PageRank top-5, HITS top-5 |
| `output/data/citation_graph.gml` | GML | Full NetworkX directed graph |

Stage 4 renders `citation_network.png` and `degree_distribution.png` from these
files; Stage 5 injects `CITATION_NODES`, `CITATION_EDGES`, `CITATION_DENSITY_PCT`,
and `CITATION_RESOLUTION_PCT` into the manuscript (see
[`visualization_guide.md`](visualization_guide.md) and
[`scripts.md`](scripts.md)). The narrative results are in
`manuscript/03d_results_citation_network.md` and
`manuscript/02c_methods_bibliometrics.md`.

## 5. Manuscript bibliography

The manuscript's bibliography is the hand-curated BibTeX file
[`manuscript/references.bib`](../manuscript/references.bib), rendered from
[`manuscript/99_references.md`](../manuscript/99_references.md). It is a separate,
curated artifact from the retrieved corpus: the BibTeX file carries the citations the
manuscript actually cites, while `corpus.jsonl` carries the retrieval snapshot. When
adding a manuscript citation, add it to `references.bib`; do not expect the pipeline
to synthesize the bibliography from the corpus.

## 6. Maintenance checklist

- Keep `CITATION.cff` version/date/DOI in step with the released snapshot.
- Never fabricate `citation_count`; a missing value stays `0`.
- Preserve the canonical-ID priority order and the deterministic title-hash fallback.
- Treat `output/data/citation_*` as generated — regenerate through the scripts rather
  than editing them by hand.

## Related documents

- [`README.md`](README.md) — documentation index
- [`architecture.md`](architecture.md) — pipeline stages and data flow
- [`data_formats.md`](data_formats.md) — corpus, nanopublication, and artifact schemas
- [`hypotheses.md`](hypotheses.md) — citation-weighted scoring formula
- [`scripts.md`](scripts.md) — per-script CLI reference
