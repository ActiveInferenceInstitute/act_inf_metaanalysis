# Testing Guide

**Repository:** [github.com/docxology/act_inf_metaanalysis](https://github.com/docxology/act_inf_metaanalysis)

## Overview

The project maintains **651 collected tests** across the test suite (**650 passed, 1 skipped** in the latest full run), achieving coverage on `src/` above the 90% CI gate (**91.12%**, verified 2026-07-25). Tests run against real method implementations — no mocks, fakes, or stubs are used for core logic. API clients use `pytest-httpserver` for isolated HTTP testing with real request/response cycles. Run `uv run pytest tests/ --cov=src --cov-fail-under=90 -q` for the authoritative gate.

### Zero-Mock Practicality

We NEVER use `unittest.mock` to mock `requests.get` or `aiohttp.ClientSession`. Instead, we spin up lightweight, real HTTP servers using `pytest-httpserver`.

**Compliant Test Example (`tests/api/test_semantic_scholar.py`):**

```python
def test_s2_search_success(httpserver):
    # 1. Instruct the local server to serve a specific JSON response
    httpserver.expect_request("/graph/v1/paper/search").respond_with_json({
        "total": 1,
        "data": [{"paperId": "123", "title": "Test Paper"}]
    })

    # 2. Inject the local server URI into the client
    client = SemanticScholarClient(base_url=httpserver.url_for("/"))

    # 3. Execute real networking logic against the local port
    results = client.search("test query")
    assert results[0].raw_id == "123"
```

## Testing LLM Logic Locally

The `knowledge_graph` module relies heavily on Ollama model outputs. Testing LLM parsing logic without triggering heavy GPU inference or hanging CI pipelines is critical.

To test the LLM extraction loop (`tests/knowledge_graph/test_extraction.py`):
1. **Stub the Ollama API**: Use `pytest-httpserver` to intercept `POST /api/generate` and return a hardcoded JSON string representing a mock assertion.
2. **Test the Parser**: The test validates that the `extract_assertions()` Python logic correctly parses your hardcoded JSON into the `Assertion` Pydantic models.
3. **Never mock the LLM wrapper**: Always instantiate the real `LLMConfig(base_url=httpserver.url_for("/"))` so the real `aiohttp` or `requests` machinery is executed.

---

## Running Tests

```bash
# Full suite (from project root)
uv run python -m pytest tests/ -v

# Quick run with fail-fast
uv run python -m pytest tests/ -x -q

# Single module
uv run python -m pytest tests/test_corpus.py -v

# With coverage report
uv run python -m pytest tests/ --cov=src --cov-report=term-missing
```

## Configuration

Test settings are defined in `pyproject.toml`:

```toml
[tool.pytest.ini_options]
pythonpath = ["src"]
testpaths = ["tests"]
addopts = "-v --tb=short --strict-markers"

[tool.coverage.run]
source = ["src"]
branch = true
fail_under = 90
```

Key points:

- `pythonpath = ["src"]` — ensures `src/` modules are importable without installation
- `branch = true` — enforces branch coverage, not just line coverage
- `fail_under = 90` — CI gate at 90% minimum coverage

## Test File Inventory

### Literature Package

| Test File | Module Under Test | Test Count | Key Scenarios |
| --- | --- | --- | --- |
| `literature/test_models.py` | `models.py` | ~15 | Paper/Author/Citation creation, `canonical_id` priority, `metadata_completeness`, JSONL round-trip |
| `literature/test_corpus.py` | `corpus.py` | ~20 | Add/merge/dedup, year filtering, domain filtering, JSONL save/load, `__contains__`/`__len__` |
| `literature/test_arxiv_client.py` | `arxiv_client.py` | ~18 | XML parsing, pagination, rate limiting, retry on HTTP errors (via `pytest-httpserver`) |
| `literature/test_semantic_scholar.py` | `semantic_scholar.py` | ~22 | JSON parsing, 429 rate-limit retry with backoff, pagination, `get_paper_details`, `get_citations` |
| `literature/test_openalex_client.py` | `openalex_client.py` | ~15 | Inverted-index abstract reconstruction, cursor pagination, `get_work_by_doi` |
| `literature/test_search_runner.py` | `search_runner.py` | 10 | Relevance filter, resume/clear corpus, YAML config merge, duplicate counting |
| `literature/test_search_runner_httpserver.py` | `search_runner.py` + API clients | 3 | End-to-end search via injectable `*_base_url` (arXiv, S2, OpenAlex) |
| `literature/test_fulltext_assessment.py` | `fulltext_assessment.py` | 2 | PDF URL coverage and domain breakdown |

### Analysis Package

| Test File | Module Under Test | Test Count | Key Scenarios |
| --- | --- | --- | --- |
| `analysis/test_text_processing.py` | `text_processing.py` | ~21 | Tokenization, stopword removal, TF-IDF matrix dimensions, L2 normalization, empty document handling |
| `analysis/test_citation_network.py` | `citation_network.py` | ~18 | Graph construction, PageRank, community detection, `build_reference_index`, `resolve_citations` |
| `analysis/test_temporal_analysis.py` | `temporal_analysis.py` | ~20 | Year counts, cumulative growth, CAGR, doubling time, gap-year fill, empty input handling |
| `analysis/test_subfield_classifier.py` | `subfield_classifier.py` | ~30 | Priority-based classification (C→B→A1→A2), word-boundary matching, domain keyword coverage, `classify_corpus` |
| `analysis/test_subfield_registry.py` | `subfield_registry.py`, `subfield_defaults.py` | 4 | YAML keyword load, pattern cache rebuild, invalid entry fallback |
| `analysis/test_pipeline_runner.py` | `pipeline_runner.py` | 1 | Stage-02 artifact bundle from sample corpus |
| `analysis/test_topic_modeling.py` | `topic_modeling.py` | ~20 | NMF convergence, topic extraction, `get_document_topics` row normalization, edge cases |

### Knowledge Graph Package

| Test File | Module Under Test | Test Count | Key Scenarios |
| --- | --- | --- | --- |
| `knowledge_graph/test_schema.py` | `schema.py` | ~15 | Namespace URIs, assertion types, hypothesis categories, domain URIs |
| `knowledge_graph/test_nanopublication.py` | `nanopublication.py` | ~20 | Create/serialize/deserialize nanopubs, merge dedup (new-wins), `append_nanopubs` atomicity |
| `knowledge_graph/test_hypothesis.py` | `hypothesis.py` | ~18 | Citation-weighted scoring formula, `score_all_hypotheses`, `temporal_trend`, edge cases |
| `knowledge_graph/test_llm_prompt_parse.py` | `llm_prompts`, `llm_client` | 9 | Prompt construction, JSON parsing |
| `knowledge_graph/test_llm_assess_paper.py` | `llm_extraction` | 6 | Single-paper httpserver assessment |
| `knowledge_graph/test_llm_batch.py` | `llm_extraction`, `extraction` | 4 | Batch extraction, unified entry point |
| `knowledge_graph/test_llm_config.py` | `llm_config` | 2 | LLMConfig defaults |
| `knowledge_graph/test_llm_nanopub_resume.py` | `llm_extraction` | 5 | Nanopub checkpoint resume |
| `knowledge_graph/test_llm_max_papers.py` | `llm_extraction` | 5 | max_papers cap |
| `knowledge_graph/test_extraction.py` | `extraction.py` | ~8 | End-to-end assertion extraction coordination |
| `knowledge_graph/test_graph_builder.py` | `graph_builder.py` | ~8 | KnowledgeGraph construction and query |
| `knowledge_graph/test_query.py` | `query.py` | ~8 | Graph query helpers |

### Visualization & Scripts

| Test File | Module Under Test | Test Count | Key Scenarios |
| --- | --- | --- | --- |
| `visualization/test_field_overview.py` | `field_overview.py` | ~8 | Field summary and subfield distribution figure generation |
| `visualization/test_citation_plots.py` | `citation_plots.py` | ~8 | Citation network and degree distribution plots |
| `visualization/test_temporal_plots.py` | `temporal_plots.py` | ~8 | Growth curve and subfield timeline plots |
| `visualization/test_hypothesis_charts.py` | `hypothesis_charts.py` | ~8 | Hypothesis dashboard and evidence timeline |
| `visualization/test_advanced_plots.py` | `advanced_plots.py` | ~10 | Word cloud, PCA, heatmap, dendrogram, topics, co-occurrence |
| `visualization/test_figure_runner.py` | `figure_runner.py` | 4 | Minimal/full fixtures, citation network without GML, empty inputs |
| `visualization/test_style.py` | `style.py` | ~5 | VIZ_CONFIG palette and font size enforcement |
| `test_config_loader.py` | `config_loader.py` | 4 | Search/KG YAML loading and defaults |
| `test_scripts.py` | All 6 pipeline scripts | ~8 | `--help` parsing, argument defaults, module importability |
| `test_variables.py` | `manuscript/variables.py` | ~36 | LaTeX formatting, JSONL counting, compute_variables with full/partial/empty output, inject_variables |

## Testing Patterns

### API Client Testing with `pytest-httpserver`

All three API clients (`arxiv_client`, `semantic_scholar`, `openalex_client`) use `pytest-httpserver` to create a real local HTTP server with canned responses. This avoids mocking `requests` while still testing real HTTP behavior:

```python
def test_search_arxiv(httpserver):
    httpserver.expect_request("/api/query").respond_with_data(
        SAMPLE_ATOM_XML, content_type="application/xml"
    )
    papers = search_arxiv("test query", base_url=httpserver.url_for("/"))
    assert len(papers) > 0
```

### Visualization Testing

Visualization tests verify that:

1. Output files are created at the expected path
2. Font sizes meet the **16pt minimum floor** (checked via `matplotlib.findobj`)
3. The colorblind-safe Wong (2011) palette is applied consistently
4. Empty/edge-case inputs produce valid (if empty) figures rather than crashing

### Fixture Patterns

- **Paper factories** — Helper functions that create `Paper` objects with configurable fields
- **Temporary directories** — `tmp_path` fixture for isolated file I/O
- **HTTP servers** — `httpserver` fixture from `pytest-httpserver` for API testing
