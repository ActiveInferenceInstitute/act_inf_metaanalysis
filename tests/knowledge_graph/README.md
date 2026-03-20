# Knowledge Graph Tests (`tests/knowledge_graph/`)

Test suite for verifying the probabilistic evidence scoring, nanopublication structuring, and LLM string parsing pipelines without relying on an active network connection.

## Focus Areas

- Progressive JSON-parsing fallback logic recovering hallucinated schema breaks.
- Citation-weighted hypothesis bounds checking.
- Output validation for TriG / RDF and JSONL semantic compliance constraints.

## Running the Tests

```bash
# General run
uv run pytest tests/knowledge_graph/ -v

# Target LLM JSON recovery exactly
uv run pytest tests/knowledge_graph/test_llm_extraction.py -v
```

See **[AGENTS.md](AGENTS.md)** for detailed module logic verification protocols and data-mocking guidelines.
