# Output Data Formats

Schema reference for all pipeline output artifacts. Each file is produced by one pipeline stage and consumed by downstream stages.

---

## Stage 1: Literature Search

### `corpus.jsonl`

One JSON object per line, each representing a deduplicated paper. Fields correspond to `Paper.to_dict()` in `src/literature/models.py`.

| Field | Type | Required | Description |
| --- | --- | --- | --- |
| `title` | string | yes | Paper title |
| `abstract` | string | yes | Abstract text (empty string if unavailable) |
| `authors` | array | yes | List of `{name, affiliation, orcid}` objects |
| `year` | int or null | no | Publication year |
| `doi` | string or null | no | Digital Object Identifier |
| `arxiv_id` | string or null | no | arXiv identifier (e.g. `"2301.12345"`) |
| `s2_id` | string or null | no | Semantic Scholar paper ID |
| `openalex_id` | string or null | no | OpenAlex work ID |
| `venue` | string or null | no | Publication venue/journal |
| `citation_count` | int | yes | Number of citations (0 if unknown) |
| `references` | array | yes | List of reference ID strings |
| `publication_date` | string or null | no | ISO-8601 date (e.g. `"2023-06-15"`) |

**Canonical ID priority** (for deduplication): DOI > arXiv ID > S2 ID > OpenAlex ID > title hash.

---

## Stage 2: Meta-Analysis

### `subfield_classification.json`

Domain → paper count mapping (A/B/C taxonomy, 8 domains).

```json
{
  "A1_formal": 120,
  "A2_philosophy": 151,
  "B_tools": 269,
  "C1_neuroscience": 214,
  "C2_robotics": 173,
  "C3_language": 58,
  "C4_psychiatry": 36,
  "C5_biology": 204
}
```

### `subfield_timeline.json`

Nested dict: domain → {year → publication count}.

```json
{
  "A1_formal": {"2010": 3, "2011": 5, "2012": 8},
  "C1_neuroscience": {"2010": 1, "2011": 2, "2012": 4}
}
```

### `temporal_analysis.json`

| Field | Type | Description |
| --- | --- | --- |
| `year_counts` | object | `{year_string: count}` for each year in range (gap-years filled with 0) |
| `smoothed_annual` | object | `{year_string: smoothed_count}` 3-year moving average of annual counts |
| `cumulative` | object | `{year_string: cumulative_count}` |
| `first_year` | int | Earliest publication year |
| `last_year` | int | Latest publication year |
| `total_papers` | int | Total deduplicated papers with valid years |
| `peak_year` | int | Year with highest publication count |
| `mean_growth_rate` | float | Mean year-over-year growth rate |
| `doubling_time` | float or null | Estimated publication doubling time (null if growth ≤ 0) |
| `cagr` | float | Compound annual growth rate |

### `tfidf_data.json`

Contains all data needed for TF-IDF-based visualizations (PCA, heatmap, dendrogram, co-occurrence).

| Field | Type | Description |
| --- | --- | --- |
| `feature_names` | array of string | Vocabulary terms (columns of TF-IDF matrix) |
| `labels` | array of string | Per-document domain labels (e.g. `"A1_formal"`, `"C2_robotics"`) |
| `matrix` | array of array | Full TF-IDF matrix as nested lists `[n_docs × n_features]` |
| `doc_tokens` | array of array | Per-document token lists (for co-occurrence analysis) |

### `topics.json`

Array of topic objects from NMF decomposition:

```json
[
  {
    "topic_id": 0,
    "top_words": ["agent", "model", "agents", "learning", "policy"],
    "weights": [0.0677, 0.0575, 0.0504, 0.0423, 0.0389]
  }
]
```

### `citation_network.json`

| Field | Type | Description |
| --- | --- | --- |
| `num_nodes` | int | Number of papers in the citation graph |
| `num_edges` | int | Number of intra-corpus citation edges |
| `density` | float | Graph density |
| `avg_in_degree` | float | Average inbound citations per paper |
| `connected_components` | int | Number of weakly connected components |
| `num_communities` | int | Number of detected communities (Louvain) |
| `total_references` | int | Total reference count across all papers |
| `top_pagerank` | object | `{paper_id: score}` for top-5 papers by PageRank |
| `top_hubs` | object | `{paper_id: score}` for top-5 hub papers (HITS) |
| `top_authorities` | object | `{paper_id: score}` for top-5 authority papers (HITS) |

### `citation_graph.gml`

Full NetworkX directed graph in GML format. Node attributes:

| Attribute | Type | Description |
| --- | --- | --- |
| `id` | string | Paper canonical ID |
| `title` | string | Paper title |
| `year` | int | Publication year |
| `citation_count` | int | External citation count |

---

## Stage 3: Knowledge Graph

### `nanopublications.jsonl`

One JSON object per line, each wrapping an assertion with provenance:

| Field | Type | Description |
| --- | --- | --- |
| `nanopub_id` | string | Unique nanopub identifier (`nanopub:hex12`) |
| `assertion.assertion_id` | string | Unique assertion ID |
| `assertion.paper_id` | string | Canonical paper ID |
| `assertion.claim` | string | Natural-language reasoning text from LLM |
| `assertion.assertion_type` | string | `"supports"`, `"contradicts"`, or `"neutral"` |
| `assertion.hypothesis_id` | string | One of 8 hypothesis IDs (see [hypotheses.md](hypotheses.md)) |
| `assertion.confidence` | float | Confidence in `[0, 1]` |
| `assertion.citation_count` | int | Paper citation count (for scoring weight) |
| `attribution` | string | Pipeline attribution string |
| `created_date` | string | ISO-8601 UTC timestamp |

### `nanopublications.trig`

RDF TriG serialization of all nanopublications, compliant with the nanopub.net specification. Contains four named graphs per nanopublication (Head, Assertion, Provenance, Publication Info). This format enables interoperability with semantic web tools and SPARQL endpoints.

### `hypothesis_scores.json`

```json
{
  "FEP_UNIVERSALITY": 0.82,
  "AIF_OPTIMALITY": 1.0,
  "MARKOV_BLANKET_REALISM": 0.45,
  "PREDICTIVE_CODING": 1.0,
  "SCALABILITY": 0.7,
  "CLINICAL_UTILITY": 0.33,
  "MORPHOGENESIS": -0.1,
  "LANGUAGE_AIF": 0.0
}
```

Each value is a float in `[-1, 1]` computed via the citation-weighted scoring formula: `score(H) = (Σ_support(w) − Σ_contradict(w)) / Σ_all(w)` where `w = log(1 + citations) × confidence`.

### `hypothesis_trends.json`

Nested dict: `{hypothesis_id: {year_string: cumulative_score}}`.

### `assertion_summary.json`

| Field | Type | Description |
| --- | --- | --- |
| `total_assertions` | int | Total extracted assertions across all papers |
| `type_counts` | object | `{assertion_type: count}` (e.g. `{"supports": 20, "contradicts": 10, "neutral": 15}`) |
| `per_hypothesis` | object | `{hypothesis_id: {assertion_type: count}}` nested mapping |

---

## Stage 4: Visualization

All figures are PNG files at 300 DPI with ≥16pt fonts, saved to `output/figures/`. See [visualization_guide.md](visualization_guide.md) for descriptions and usage.
