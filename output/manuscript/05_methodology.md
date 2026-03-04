# Methodology: Pipeline Design and Formal Definitions

This section describes the five-stage computational meta-analysis pipeline. Each stage corresponds to a tested, independently executable script that reads upstream outputs and produces structured artifacts. The pipeline extends the systematic literature analysis approach of Knight et al. \citep{knight2022fep}—which combined manual annotation with ontology-based automated analysis—by substituting manual coding with fully automated, LLM-driven assertion extraction and citation-weighted hypothesis scoring.

## Pipeline Overview

| Stage | Script | Primary Input | Primary Output | Section |
| --- | --- | --- | --- | --- |
| 1 | `01_literature_search.py` | API queries | `corpus.jsonl` | §5.1 |
| 2 | `02_meta_analysis_pipeline.py` | `corpus.jsonl` | Classification, temporal, TF-IDF, NMF, citation network JSONs | §5.2 |
| 3 | `03_build_knowledge_graph.py` | `corpus.jsonl` | `nanopublications.jsonl`, `nanopublications.trig`, scores | §5.3 |
| 4 | `04_generate_figures.py` | All Stage 2–3 JSONs | 16 publication-ready PNGs | §5.4 |
| 5 | `05_inject_variables.py` | All output JSONs | Rendered manuscript Markdown | §5.5 |

Scripts act as thin orchestrators that import methods from tested library modules and handle file I/O. All computation resides in the `src/` packages; no analysis logic is embedded in scripts.

## Stage 1: Multi-Source Literature Retrieval and Deduplication

We retrieve papers from three complementary academic databases to maximize coverage and enable cross-source deduplication:

**arXiv.** We query the arXiv Atom API using phrase-matched searches including `all:"active inference"`, `all:"free energy principle"`, `all:"expected free energy"`, `all:"variational free energy" AND all:"inference"`, and targeted Energy-Based Model queries (`all:"energy-based model" AND all:"free energy"`, `all:"Helmholtz machine" AND all:"inference"`, `all:"Boltzmann machine" AND all:"free energy"`, `all:"contrastive divergence" AND all:"generative model"`). The `all:` prefix searches titles, abstracts, and full text; phrase matching reduces contamination from unrelated physics papers that mention "free energy" in thermodynamic contexts. The EBM-adjacent queries capture research at the intersection of energy-based generative modeling and variational inference—a growing convergence area \citep{lecun2006tutorial}.

**Semantic Scholar.** We query the Semantic Scholar Graph API \citep{kinney2023semantic} with the same terms. Semantic Scholar provides citation graphs, abstract embeddings, and links to published versions. Retry logic with exponential backoff handles rate limiting.

**OpenAlex.** We query OpenAlex \citep{priem2022openalex} to capture journal-published work that may not appear on arXiv, including clinical studies and neuroscience experiments in domain-specific venues. The `referenced_works` field populates citation links for each paper.

### Canonical Identifier Deduplication

<<<<<<< HEAD
After retrieval, papers are assigned a canonical identifier using the priority scheme: DOI $>$ arXiv ID $>$ Semantic Scholar ID $>$ OpenAlex ID $>$ title hash. When the same paper appears in multiple sources, the record with the highest metadata completeness is retained. For each incoming paper, the two records are comparatively evaluated on metadata completeness—defined as the count of non-empty attributes among \{abstract, DOI, arXiv ID, venue, citation count\}. The pipeline reliably retains the structurally richer record; in the event of a tie, the incumbent is preserved. This "merge-on-add" strategy automatically aggregates the richest available metadata without mandating an expensive downstream reconciliation pass. Deduplication produces $N = 785$ unique papers spanning 1977--2026.

### Relevance Filtering and Curation

After deduplication, a **relevance filter** removes papers whose titles and abstracts lack any core Active Inference terminology (e.g., ``active inference,''``free energy principle,'' ``variational free energy''), eliminating off-topic results introduced by broad keyword overlap across heterogeneous databases.

We emphasize that this process relies fundamentally on keyword search strategies across divergent APIs. In any complex research field, there is no single optimal word or threshold for definitive inclusion or exclusion. Different information sources and repositories yield differing schemas and representations, inevitably introducing both false positives (extraneous papers overlapping in terminology, such as unrelated database or biological toolkits) and false negatives (relevant papers employing alternative nomenclature without standard keywords).
=======
After retrieval, papers are assigned a canonical identifier using the priority scheme: DOI $>$ arXiv ID $>$ Semantic Scholar ID $>$ OpenAlex ID $>$ title hash. When the same paper appears in multiple sources, the record with the highest metadata completeness is retained. For each incoming paper, the two records are compared on metadata completeness—defined as the count of non-empty attributes among \{abstract, DOI, arXiv ID, venue, citation count\}. The pipeline retains the richer record; in the event of a tie, the incumbent is preserved. This "merge-on-add" strategy aggregates the richest available metadata without requiring an expensive downstream reconciliation pass. Deduplication produces $N = 785$ unique papers spanning 1977–2026.

### Relevance Filtering and Curation

After deduplication, a **relevance filter** removes papers whose titles and abstracts lack any core Active Inference terminology (e.g., ``active inference,''``free energy principle,'' ``variational free energy''), eliminating off-topic results introduced by broad keyword overlap across heterogeneous databases.

We emphasize that this process relies on keyword search strategies across divergent APIs. In any complex research field, there is no single optimal word or threshold for definitive inclusion or exclusion. Different information sources and repositories yield differing schemas and representations, introducing both false positives (papers overlapping in terminology, such as unrelated database or biological toolkits) and false negatives (relevant papers using alternative nomenclature without standard keywords).
>>>>>>> 042a14f (refine: scholarly prose, fix stale data, remove unused refs)

Consequently, this pipeline is not intended to produce a static, "golden" list of canonical papers. Rather, it is designed as an open-source software package that can be modularly updated and versioned. Researchers can configure the pipeline to operate on custom literature bibliographies curated for specific relevance criteria through time, treating the initial query-based retrieval as a programmatic starting point rather than an absolute boundary.

## Stage 2: Bibliometric Analysis

Stage 2 performs four complementary analyses on the deduplicated corpus. All analyses are deterministic given fixed random seeds and operate on the same `corpus.jsonl` input.

### Subfield Classification

Each paper is classified into one of eight categories organized across three domains: **A – Core Theory** (A1: quantitative and formal mathematical theory; A2: qualitative philosophy and general FEP theory), **B – Tools \& Translation** (algorithms, scaling, and software development), and **C – Application Domains** (C1: neuroscience, C2: robotics, C3: language processing, C4: computational psychiatry, C5: biology and morphogenesis). Classification uses word-boundary-aware keyword matching against curated lists applied to titles and abstracts. A priority system ensures that specific application domains (C1–C5, priority 1) take precedence over tools (B, priority 2), formal theory (A1, priority 3), and the broad qualitative philosophy catch-all (A2, priority 4). Within a priority tier, the domain with the most keyword matches wins. A1's keyword set includes mathematical indicators such as *theorem*, *proof*, *convergence*, *posterior*, *equation*, and *Fokker–Planck*, ensuring that papers with mathematical content are classified as formal theory rather than defaulting to the philosophy category.

### Temporal Metrics and Growth-Rate Estimation

We compute temporal publication metrics including year-by-year counts with gap-filling, cumulative totals, 3-year smoothed moving averages, and peak year identification. Field dynamics are estimated via two complementary metrics. The **mean year-over-year growth rate** $\bar{g}$ is the arithmetic mean of annual growth rates for years with non-zero prior-year publications. The **doubling time** $t_d = \ln 2 / \ln(1 + \bar{g})$. The **compound annual growth rate** (CAGR) captures the annualized rate across the full temporal span. Mathematical details are provided in the Technical Appendix (A.3).

### Text Analytics

The TF-IDF matrix is constructed manually using tokenization with stopword removal and L2-normalized term-frequency inverse-document-frequency weighting \citep{salton1975vector}, with a configurable vocabulary size (default: 1000 features). Non-negative matrix factorization (NMF) is applied to discover latent topics using multiplicative update rules \citep{lee1999nmf}. Mathematical details are provided in the Technical Appendix (A.2).

### Citation Network Construction

The intra-corpus citation network is constructed as a directed graph where nodes are papers and edges represent citation relationships resolved within the corpus. Network metrics include PageRank centrality, HITS hub and authority scores \citep{kleinberg1999authoritative}, degree distributions, network density, connected components, and community structure via the Louvain algorithm \citep{blondel2008louvain}.

## Stage 3: Nanopublication-Based Knowledge Graph

Stage 3 is the methodological core of this work: it transforms unstructured abstracts into a structured, RDF-compatible knowledge graph of scientific evidence. The stage encompasses four tightly coupled operations: LLM-based assertion extraction, nanopublication packaging, knowledge graph construction, and citation-weighted hypothesis scoring.

### LLM-Based Assertion Extraction

We extract assertions by prompting a locally hosted LLM (Ollama \citep{ollama2024}) to assess each paper's abstract against eight standard hypotheses. The model receives a structured prompt containing the paper title, abstract, and hypothesis definitions, and returns a JSON array where each element specifies a hypothesis ID, direction (supports, contradicts, neutral, or irrelevant), a confidence score $c \in [0, 1]$, and a reasoning string. Assertions marked "irrelevant" are discarded; confidence values are clamped to $[0, 1]$; and responses are validated against the known hypothesis ID set. Papers lacking abstracts are skipped. Detailed prompt engineering, error taxonomy, and validation methodology are documented in Section 3.

### Nanopublication Schema and RDF Structure

Each assertion is encoded as a **nanopublication** \citep{groth2010anatomy, kuhn2016decentralized}—a minimal, self-contained, machine-readable unit of scientific evidence. Formally, each nanopublication is a tuple $(p, h, d, c)$ where $p$ is the paper identifier, $h$ the hypothesis identifier, $d \in \{\text{supports}, \text{contradicts}, \text{neutral}\}$ the direction, and $c$ the confidence. Provenance metadata records the LLM model, UTC timestamp, and paper identifier.

The pipeline serializes nanopublications in two complementary formats:

1. **JSON Lines** (one JSON object per line) for efficient incremental checkpointing. Assertions are saved at configurable intervals (default: every 50 papers), enabling the pipeline to resume from where it left off after interruption without re-processing already-analyzed papers. Deduplication uses the composite key $(paper\_id, hypothesis\_id)$; re-runs with improved models overwrite stale results.

2. **RDF/TriG** per the nanopublication standard (<https://nanopub.net/>), producing four named graphs per nanopublication:

| Named Graph | Content | Key Predicates |
| --- | --- | --- |
| **Head** | Links the nanopub resource to its three component graphs | `np:hasAssertion`, `np:hasProvenance`, `np:hasPublicationInfo` |
| **Assertion** | The core scientific claim | `aif:asserts` (Paper → Assertion), `aif:supports`/`aif:contradicts` (Assertion → Hypothesis), `aif:claim`, `aif:confidence`, `aif:citationCount` |
| **Provenance** | How the assertion was generated | `prov:wasGeneratedBy`, `prov:generatedAtTime`, `prov:wasAttributedTo`, `prov:hadPrimarySource` |
| **Publication Info** | Metadata about the nanopublication itself | `dc:created`, `dc:creator`, `dc:license` |

The namespace `http://activeinference.org/ontology/` (prefix `aif:`) defines all domain predicates; the nanopublication schema (`http://www.nanopub.org/nschema#`, prefix `np:`) provides structural predicates; provenance uses PROV-O (`http://www.w3.org/ns/prov#`); and Dublin Core (`http://purl.org/dc/terms/`) provides publication metadata. The TriG output is suitable for publication to the decentralized nanopublication network and aligns with FAIR data principles: **F**indable via URI-based identification, **A**ccessible via standard RDF protocols, **I**nteroperable through W3C-standard serialization, and **R**eusable with explicit provenance and CC0 licensing.

### Knowledge Graph Construction

The knowledge graph is an RDF-compatible directed graph with three node types: **paper nodes** (metadata: title, abstract, authors, year, venue, citation count, domain), **assertion nodes** (claim text, direction, hypothesis ID, confidence), and **hypothesis nodes** (the eight standard hypotheses). Edges encode five relations defined in the schema:

- `aif:asserts` — Paper $\to$ Assertion
- `aif:cites` — Paper $\to$ Paper
- `aif:belongsTo` — Paper $\to$ Subfield
- `aif:supports` — Assertion $\to$ Hypothesis
- `aif:contradicts` — Assertion $\to$ Hypothesis

The graph is implemented with a dual backend: `rdflib` \citep{rdflib2023} when available (preferred for semantic web compatibility), with automatic fallback to `networkx.DiGraph` for environments without RDF dependencies. Both backends maintain identical internal indices for efficient paper, assertion, and hypothesis queries.

### Citation-Weighted Hypothesis Scoring

For each hypothesis $H$, we compute a citation-weighted evidence score:

$$
\text{score}(H) = \frac{\sum_{a \in S(H)} w(a) - \sum_{a \in C(H)} w(a)}{\sum_{a \in A(H)} w(a)}
$$

where $S(H)$, $C(H)$, and $A(H)$ are the sets of supporting, contradicting, and all assertions for $H$, and the weight function is:

$$
w(a) = \log(1 + \text{citations}(a)) \cdot \text{confidence}(a)
$$

The logarithmic citation weighting ensures that highly cited papers carry more influence without allowing any single paper to dominate. The score lies in $[-1, 1]$. Temporal trends are computed by evaluating the cumulative score at each year, using only assertions from papers published up to that year. A full derivation appears in the Technical Appendix (A.1).

### Tally-Based Evidence Aggregation

We emphasize that this algorithmic scoring formula constitutes a **tally-based approach** to evidence synthesis: each nanopublication assertion operates as an independent evidential vote, weighted by citation impact and the extraction model's confidence. The aggregation is linear and additive—supporting and contradicting assertions are summed and differenced without modeling dependencies, correlated evidence, or causal structure among claims. This design choice prioritizes transparency, reproducibility, and computational tractability over statistical sophistication.

The tally-based framing introduces three constraints. First, assertions from methodologically related papers (e.g., iterative publications from a single research group testing the same model) are counted independently, amplifying correlated evidence. Second, the scoring metric treats all assertion sources symmetrically: an assertion from a theoretical review and one from an empirical trial carry equal weight at a given confidence level. Third, temporal scoring tracks *cumulative totals* rather than dynamic probabilistic estimates; the score at year $t$ is the sum of all historical evidence, rather than a decaying posterior that downweights early work.

We embrace these constraints intentionally. The tally-based approach provides a stable, interpretable baseline against which more sophisticated scoring methods can be evaluated. Section 8 describes concrete extensions—including hierarchical Bayesian scoring, causal evidence graphs, and evidential diversity indices that downweight correlated evidence.

## Stage 4: Visualization

Stage 4 renders 16 publication-ready figures from the analysis outputs of Stages 2 and 3. All figures use the Wong (2011) colorblind-safe palette \citep{wong2011colorblind} and enforce a 16-point minimum font size for accessibility compliance. Figures span six categories: field summary and domain distribution (2 figures), growth and temporal dynamics (2 figures), citation network topology (2 figures), hypothesis evidence dashboard and timeline (2 figures), assertion composition (2 figures), and text analytics—word cloud, PCA embeddings, term heatmap, dendrogram, topic-term bars, and co-occurrence matrix (6 figures). The figure generation script reads only JSON outputs and produces only PNG files, ensuring strict separation between analysis and visualization.

## Stage 5: Manuscript Variable Injection

Stage 5 computes dynamic variables from all pipeline outputs and injects them into manuscript Markdown templates via `{{VAR_NAME}}` placeholder substitution. Variables include corpus-level metrics (size, year range, CAGR), per-domain counts and percentages, citation network statistics (nodes, edges, density, components, resolution rate, mean in-degree), hypothesis scores, and figure counts. All LaTeX-specific formatting (thousand separators via `{,}`, escaping) is applied during variable computation, ensuring the manuscript templates remain human-readable while producing publication-ready LaTeX output. Unrecognized placeholders are preserved with a warning logged, enabling incremental manuscript development ahead of full pipeline execution.

## Reproducibility and Test-Driven Validation

The pipeline is deterministic given fixed random seeds and API responses. Test-driven development enforces 90\% minimum code coverage on project modules and 60\% on shared infrastructure, with real data and computation (no mocking). The test suite validates boundary conditions for hypothesis scoring (all-support $\to$ +1, all-contradict $\to$ $-1$, balanced $\to$ 0), schema consistency, serialization round-trips, and end-to-end pipeline integrity. Source code, configuration, and outputs are available under CC-BY-4.0.
