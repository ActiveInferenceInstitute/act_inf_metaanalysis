# API Reference

**Repository:** [github.com/ActiveInferenceInstitute/act_inf_metaanalysis](https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis)

Public API for the five packages in `src/`. The pipeline tracks **8 hypotheses** and renders **16 figures**; corpus size and assertion counts evolve with each run (see the latest `output/data/temporal_analysis.json` and `output/data/assertion_summary.json` for current numbers).

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
    pdf_url: Optional[str] = None             # Direct PDF URL when known (arXiv, OA repos)
    is_open_access: Optional[bool] = None     # OA flag from OpenAlex/S2 best_oa_location
    full_text_source: Optional[str] = None    # Provenance label, e.g. "arxiv", "openalex"

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

**Usage Example:**

```python
from literature.corpus import Corpus
from literature.arxiv_client import search_arxiv

# Create a fresh corpus, run a small query, and add papers
corpus = Corpus()
new_papers = search_arxiv(query="active inference", max_results=10)
for p in new_papers:
    corpus.add(p)

print(f"Corpus contains {len(corpus)} unique papers.")
```

### Literature search orchestration (`literature.search_runner`)

```python
def search_source(
    source_name: str,
    search_fn: Callable[..., list[Paper]],
    query: str,
    max_results: int,
    corpus: Corpus,
    logger: logging.Logger,
) -> str | None

def apply_relevance_filter(corpus: Corpus, keywords: list[str], logger: logging.Logger) -> None

def run_literature_search(
    args: argparse.Namespace,
    *,
    project_root: Path,
    arxiv_base_url: str | None = None,
    semantic_scholar_base_url: str | None = None,
    openalex_base_url: str | None = None,
) -> Path
```

`run_literature_search` is invoked by `scripts/01_literature_search.py`. Optional `*_base_url` kwargs wire
`pytest-httpserver` endpoints into API clients for integration tests.

## analysis

Bibliometric and text analysis.

### Text Processing (`analysis.text_processing`)

```python
def tokenize(text: str) -> list[str]
def remove_stopwords(tokens: list[str], extra_stopwords: set[str] | None = None) -> list[str]
def build_tfidf_matrix(documents: list[str], max_features: int = 1000) -> tuple[np.ndarray, list[str]]
```

### Domain Classifier (`analysis.subfield_classifier`, `subfield_registry`, `subfield_defaults`)

Keyword data and compiled regex cache live in `subfield_defaults` / `subfield_registry`; import the public API from `subfield_classifier`.

```python
SUBFIELDS: dict[str, dict]  # 8 domain entries with 'keywords', 'description', and 'priority'

def classify_paper(paper: Paper) -> str  # Priority-aware; returns domain name (e.g. "A1_formal")
def classify_corpus(papers: list[Paper], config_path: Optional[Path] = None) -> dict[str, list[Paper]]
def configure_subfields(config_path: Optional[Path] = None) -> None
```

### Citation Network (`analysis.citation_network`)

```python
def build_citation_graph(papers: list[Paper], citations: list[Citation]) -> nx.DiGraph
def compute_network_metrics(
    graph: nx.DiGraph,
    hits_max_iter: int = 200,
    hits_tol: float = 1e-06,
) -> dict
    # Returns: 
    #   num_nodes: Total nodes
    #   num_edges: Total edges
    #   density: Network density
    #   avg_in_degree: Average inbound citations 
    #   avg_out_degree: Average outbound references
    #   pagerank: Dict mapping top-5 paper_id -> score
    #   hubs: Dict mapping top-5 paper_id -> score (often review papers)
    #   authorities: Dict mapping top-5 paper_id -> score (often foundational methods)
    #   connected_components: Number of weakly connected components
def detect_communities(graph: nx.DiGraph) -> dict[str, int]  # node_id -> community_id

def build_reference_index(papers: list[Paper]) -> dict[str, str]  # raw_id -> canonical_id
def resolve_citations(papers: list[Paper], ref_index: dict[str, str], logger: logging.Logger) -> list[Citation]
```

### Temporal Analysis (`analysis.temporal_analysis`)

```python
def compute_temporal_metrics(papers: list[Paper]) -> dict
    # Returns: 
    #   year_counts: Dict[str, int]
    #   smoothed_annual: Dict[str, float] (3-year moving avg)
    #   cumulative: Dict[str, int]
    #   first_year/last_year: Int bounds
    #   total_papers: Total valid
    #   peak_year: Int of highest volume year

def estimate_growth_rate(year_counts: dict[int, int]) -> dict
    # Returns: 
    #   annual_growth_rates: Dict[int, float]
    #   mean_growth_rate: float
    #   doubling_time: float (in years, null if growth <= 0)
    #   cagr: float (Compound Annual Growth Rate)
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
AIF_NAMESPACE: str = "http://activeinference.institute/ontology/"
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

**Usage Example:**

```python
from knowledge_graph.llm_extraction import LLMConfig
from knowledge_graph.extraction import extract_assertions
from literature.corpus import Corpus
from pathlib import Path

corpus = Corpus.load(Path("output/data/corpus.jsonl"))

# Configure Ollama integration (resumes automatically if nanopub_path exists)
config = LLMConfig(
    base_url="http://localhost:11434",
    model="gemma3:4b", 
    nanopub_path="output/nanopublications.jsonl",
    checkpoint_interval=10
)

# Extracts assertions only for papers not already present in the nanopub_path
assertions = extract_assertions(corpus.papers, llm_config=config)
print(f"Extracted {len(assertions)} total assertions.")
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
    # (e.g., "CORPUS_SIZE" -> the current corpus count formatted for LaTeX) ready for injection.

def inject_variables(
    content: str,
    variables: dict[str, str],
    filename: str = "<unknown>",
) -> str:
    # Replaces all {{VAR_NAME}} placeholders in the markdown content
    # with their corresponding computed values. Returns the injected string.
```
