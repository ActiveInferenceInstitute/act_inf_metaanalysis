# API Reference

Public API for the five packages in `src/`.

## literature

Paper retrieval and corpus management.

### Data Models (`literature.models`)

```python
@dataclass
class Author:
    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None

@dataclass
class Citation:
    source_id: str
    target_id: str
    context: Optional[str] = None

@dataclass
class Paper:
    title: str
    abstract: str = ""
    authors: list[Author] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    s2_id: Optional[str] = None
    openalex_id: Optional[str] = None
    venue: Optional[str] = None
    citation_count: int = 0
    references: list[str] = field(default_factory=list)
    publication_date: Optional[date] = None

    @property
    def canonical_id(self) -> str  # Priority: doi > arxiv_id > s2_id > openalex_id > title hash

    @property
    def metadata_completeness(self) -> int  # Count of non-None optional fields

    def to_dict(self) -> dict
    @classmethod
    def from_dict(cls, data: dict) -> Paper
```

### arXiv Client (`literature.arxiv_client`)

```python
def search_arxiv(
    query: str,
    max_results: int = 100,
    base_url: str = ARXIV_API_URL,
    session: Optional[requests.Session] = None,
    rate_limit_seconds: float = 3.0,
) -> list[Paper]

def parse_arxiv_response(xml_text: str) -> list[Paper]
```

### Semantic Scholar Client (`literature.semantic_scholar`)

```python
def search_semantic_scholar(
    query: str,
    max_results: int = 100,
    base_url: str = "https://api.semanticscholar.org/graph/v1",
    session: requests.Session | None = None,
) -> list[Paper]

def get_paper_details(paper_id: str, ...) -> Paper
def get_citations(paper_id: str, ...) -> list[Citation]
```

### OpenAlex Client (`literature.openalex_client`)

```python
def search_openalex(
    query: str,
    max_results: int = 100,
    base_url: str = "https://api.openalex.org",
    session: requests.Session | None = None,
) -> list[Paper]

def get_work_by_doi(doi: str, ...) -> Paper
```

### Corpus (`literature.corpus`)

```python
class Corpus:
    def __init__(self, papers: Optional[list[Paper]] = None) -> None

    @property
    def papers(self) -> list[Paper]

    def add(self, paper: Paper) -> None
    def merge(self, other: Corpus) -> None
    def get(self, canonical_id: str) -> Optional[Paper]
    def __len__(self) -> int
    def __contains__(self, canonical_id: str) -> bool
    def filter_by_year(self, start: Optional[int] = None, end: Optional[int] = None) -> Corpus
    def filter_by_subfield(self, subfield: str) -> Corpus
    def save(self, path: Path) -> None  # JSONL format
    @classmethod
    def load(cls, path: Path) -> Corpus
```

## analysis

Bibliometric and text analysis.

### Text Processing (`analysis.text_processing`)

```python
def tokenize(text: str) -> list[str]
def remove_stopwords(tokens: list[str], extra_stopwords: set[str] | None = None) -> list[str]
def build_tfidf_matrix(documents: list[str], max_features: int = 1000) -> tuple[np.ndarray, list[str]]
```

### Domain Classifier (`analysis.subfield_classifier`)

```python
SUBFIELDS: dict[str, dict]  # 8 domain entries with 'keywords', 'description', and 'priority'

def classify_paper(paper: Paper) -> str  # Priority-aware; returns domain name (e.g. "A1_formal")
def classify_corpus(papers: list[Paper], config_path: Optional[Path] = None) -> dict[str, list[Paper]]
```

### Citation Network (`analysis.citation_network`)

```python
def build_citation_graph(papers: list[Paper], citations: list[Citation]) -> nx.DiGraph
def compute_network_metrics(
    graph: nx.DiGraph,
    hits_max_iter: int = 200,
    hits_tol: float = 1e-06,
) -> dict
    # Returns: num_nodes, num_edges, density, avg_in_degree, avg_out_degree,
    #          pagerank, hubs, authorities, connected_components
def detect_communities(graph: nx.DiGraph) -> dict[str, int]  # node_id -> community_id
def build_reference_index(papers: list[Paper]) -> dict[str, str]  # raw_id -> canonical_id
def resolve_citations(papers: list[Paper], ref_index: dict[str, str], logger: logging.Logger) -> list[Citation]
```

### Temporal Analysis (`analysis.temporal_analysis`)

```python
def compute_temporal_metrics(papers: list[Paper]) -> dict
    # Returns: year_counts, smoothed_annual, cumulative, first_year, last_year, total_papers, peak_year

def estimate_growth_rate(year_counts: dict[int, int]) -> dict
    # Returns: annual_growth_rates, mean_growth_rate, doubling_time, cagr
```

### Topic Modeling (`analysis.topic_modeling`)

```python
def fit_nmf_topics(
    tfidf_matrix: np.ndarray,
    feature_names: list[str],
    n_topics: int = 5,
    seed: int = 42,
    top_n: int = 10,
    max_iter: int = 200,
) -> list[dict]
    # Returns list of {topic_id, top_words, weights}

def get_document_topics(
    tfidf_matrix: np.ndarray,
    n_topics: int = 5,
    seed: int = 42,
    max_iter: int = 200,
) -> np.ndarray
    # Returns (n_docs, n_topics) matrix with L1-normalized rows
```

## knowledge_graph

RDF knowledge graph and hypothesis scoring.

### Schema (`knowledge_graph.schema`)

```python
AIF_NAMESPACE: str = "http://activeinference.org/ontology/"
ASSERTION_TYPES: dict[str, str]  # predicate name -> URI
DEFAULT_HYPOTHESIS_CATEGORIES: dict[str, str]  # default 8 hypothesis URIs
HYPOTHESIS_CATEGORIES: dict[str, str]  # active hypothesis_id -> URI (configurable)
SUBFIELD_URIS: dict[str, str]  # domain_name -> URI

def configure_hypothesis_categories(hypothesis_ids: list[str]) -> dict[str, str]
    # Rebuild HYPOTHESIS_CATEGORIES from arbitrary hypothesis ID list
```

### Nanopublication (`knowledge_graph.nanopublication`)

```python
@dataclass
class Assertion:
    assertion_id: str
    paper_id: str
    claim: str
    assertion_type: str  # "supports" | "contradicts" | "neutral"
    hypothesis_id: str   # key from HYPOTHESIS_CATEGORIES
    confidence: float = 1.0  # [0, 1]
    citation_count: int = 0

@dataclass
class Nanopublication:
    nanopub_id: str
    assertion: Assertion
    attribution: str = ""
    created_date: str = ""

def create_nanopub(assertion: Assertion, attribution: str = "") -> Nanopublication
def nanopub_to_dict(nanopub: Nanopublication) -> dict
def nanopub_from_dict(data: dict) -> Nanopublication
def serialize_nanopubs(nanopubs: list[Nanopublication], path: Path) -> None
def deserialize_nanopubs(path: Path) -> list[Nanopublication]
def merge_nanopubs(existing: list[Nanopublication], new: list[Nanopublication]) -> list[Nanopublication]
def get_processed_paper_ids(nanopubs: list[Nanopublication]) -> set[str]
def append_nanopubs(new_nanopubs: list[Nanopublication], path: Path) -> list[Nanopublication]
    # Atomic read-merge-write with deduplication by (paper_id, hypothesis_id)
```

### Hypothesis Scoring (`knowledge_graph.hypothesis`)

```python
@dataclass
class Hypothesis:
    hypothesis_id: str
    name: str
    description: str

STANDARD_HYPOTHESES: list[Hypothesis]  # 8 default hypotheses (hardcoded fallback)
HYPOTHESES: list[Hypothesis]  # active hypothesis set (configurable)

def load_hypotheses_from_config(config_path: Path) -> list[Hypothesis]
    # Load hypothesis definitions from YAML config

def configure_hypotheses(config_path: Optional[Path] = None) -> list[Hypothesis]
    # Set module-level HYPOTHESES from config or defaults;
    # also updates HYPOTHESIS_CATEGORIES in schema.py

def score_hypothesis(assertions: list[Assertion], hypothesis_id: str) -> float
    # Returns score in [-1.0, 1.0]

def score_all_hypotheses(assertions: list[Assertion]) -> dict[str, float]
    # Scores all configured hypotheses

def get_hypothesis_by_id(hypothesis_id: str) -> Optional[Hypothesis]

def temporal_trend(
    assertions: list[Assertion],
    hypothesis_id: str,
    papers: list[Paper],
) -> dict[int, float]  # year -> cumulative score
```

### Graph Builder (`knowledge_graph.graph_builder`)

```python
class KnowledgeGraph:
    def __init__(self, use_rdflib: Optional[bool] = None) -> None  # Auto-detects rdflib
    def add_paper(self, paper: Paper) -> None
    def add_assertion(self, assertion: Assertion) -> None
    def add_citation(self, source_id: str, target_id: str) -> None
    def add_subfield(self, paper_id: str, subfield: str) -> None
    def num_triples(self) -> int
    def get_papers(self) -> list[str]
    def get_assertions_for_paper(self, paper_id: str) -> list[str]  # Returns assertion IDs
    def get_papers_for_hypothesis(self, hypothesis_id: str) -> list[str]
    def to_networkx(self) -> nx.DiGraph
```

### Query Helpers (`knowledge_graph.query`)

```python
def query_papers_by_hypothesis(kg: KnowledgeGraph, hypothesis_id: str) -> list[str]
def query_assertions_for_paper(kg: KnowledgeGraph, paper_id: str) -> list[str]
def query_supporting_papers(kg: KnowledgeGraph, hypothesis_id: str) -> list[str]
def query_contradicting_papers(kg: KnowledgeGraph, hypothesis_id: str) -> list[str]
def count_triples_by_type(kg: KnowledgeGraph) -> dict[str, int]
```

### LLM Extraction (`knowledge_graph.llm_extraction`)

```python
@dataclass
class LLMConfig:
    base_url: str = "http://localhost:11434"
    model: str = "gemma3:4b"
    temperature: float = 0.1
    max_tokens: int = 2048
    timeout_seconds: int = 120
    max_retries: int = 3
    retry_delay: float = 2.0
    nanopub_path: str | None = None         # JSONL file for incremental persistence
    checkpoint_interval: int = 50           # Papers between disk flushes
    max_papers: int | None = None           # None = process all papers

def build_prompt(paper: Paper, hypotheses: list[dict[str, str]]) -> str
    # Constructs system+user prompt for LLM assessment

def assess_paper_hypotheses(paper: Paper, config: LLMConfig) -> list[Assertion]
    # Sends one paper to LLM, parses JSON response, returns Assertions

def extract_assertions_llm(
    papers: list[Paper],
    config: LLMConfig | None = None,
) -> list[Assertion]
    # Incremental batch extraction: reads existing nanopubs from nanopub_path,
    # skips already-processed papers, flushes new assertions at checkpoint_interval
```

### Assertion Extraction Dispatcher (`knowledge_graph.extraction`)

```python
def extract_assertions(
    papers: list[Paper],
    llm_config: LLMConfig | None = None,
) -> list[Assertion]
    # Dispatches to extract_assertions_llm() with provided config
```

## visualization

Publication-ready figure generation.

### Style (`visualization.style`)

```python
VIZ_CONFIG: dict  # palette, figsize, dpi, font settings (colorblind-safe)
```

### Field Overview (`visualization.field_overview`)

```python
def plot_field_summary(total_papers: int, subfield_counts: dict[str, int], output_path: Path) -> Path
def plot_subfield_distribution(subfield_counts: dict[str, int], output_path: Path) -> Path
```

### Citation Plots (`visualization.citation_plots`)

```python
def plot_citation_network(graph: nx.DiGraph, output_path: Path) -> Path
def plot_degree_distribution(graph: nx.DiGraph, output_path: Path) -> Path
```

### Temporal Plots (`visualization.temporal_plots`)

```python
def plot_growth_curve(
    year_counts: dict[int, int],
    cumulative: dict[int, int],
    output_path: Path,
) -> Path

def plot_subfield_timeline(
    subfield_year_counts: dict[str, dict[int, int]],
    output_path: Path,
) -> Path
```

### Hypothesis Charts (`visualization.hypothesis_charts`)

```python
def plot_hypothesis_dashboard(scores: dict[str, float], output_path: Path) -> Path
def plot_evidence_timeline(yearly_scores: dict[str, dict[int, float]], output_path: Path) -> Path
def plot_assertion_type_breakdown(
    assertion_counts: dict[str, dict[str, int]],
    output_path: Path,
) -> Path
    # Per-hypothesis stacked bars of supports/contradicts/neutral
def plot_assertion_summary(
    total_assertions: int,
    type_counts: dict[str, int],
    hypothesis_counts: dict[str, int],
    output_path: Path,
) -> Path
    # Multi-panel summary of all assertion statistics
```

### Advanced Plots (`visualization.advanced_plots`)

```python
def plot_word_cloud(
    word_weights: dict[str, float],
    output_path: Path,
    *,
    max_words: int = 100,
) -> Path
    # Word cloud from term weights (e.g. mean TF-IDF)

def plot_pca_embeddings(
    tfidf_matrix: np.ndarray,
    labels: list[str],
    feature_names: list[str],
    output_path: Path,
    *,
    n_loading_arrows: int = 8,
) -> Path
    # 2-D PCA scatter colored by domain with loading arrows

def plot_term_heatmap(
    tfidf_matrix: np.ndarray,
    feature_names: list[str],
    labels: list[str],
    output_path: Path,
    *,
    n_terms: int = 20,
) -> Path
    # Mean TF-IDF weight heatmap for top terms × domains

def plot_dendrogram(
    tfidf_matrix: np.ndarray,
    labels: list[str],
    output_path: Path,
) -> Path
    # Ward-linkage hierarchical clustering of domain centroids

def plot_topic_term_bars(
    topics: list[dict],
    output_path: Path,
) -> Path
    # Faceted horizontal bar charts of top terms per NMF topic

def plot_cooccurrence_matrix(
    documents: list[list[str]],
    output_path: Path,
    *,
    n_terms: int = 30,
) -> Path
    # Symmetric heatmap of term co-occurrence across documents
```

## manuscript

Variable computation and dynamic manuscript management.

### Variables (`manuscript.variables`)

```python
def compute_variables(output_dir: Path) -> dict[str, str]:
    # Reads pipeline JSON outputs and returns a dictionary of template variables
    # (e.g., "CORPUS_SIZE" -> "1{,}204") ready for LaTeX injection.

def inject_variables(
    content: str,
    variables: dict[str, str],
    filename: str = "<unknown>",
) -> str:
    # Replaces all {{VAR_NAME}} placeholders in the markdown content
    # with their corresponding computed values. Returns the injected string.
```
