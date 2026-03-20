# Test Suite (`tests/`)

The rigorous testing infrastructure for the Active Inference Meta-Analysis pipeline. The codebase strictly avoids mocking, instead relying on realistic data payloads and local HTTP servers to guarantee end-to-end integration coherency representing over 534 unit and integration tests.

## 🚀 Quick Start

Ensure you are operating within a synchronized `uv` environment. The project validates against Python 3.12+.

```bash
# Execute the entire test suite and verify ≥90% coverage threshold
uv run pytest tests/ --cov=src --cov-fail-under=90 -v

# Run tests for a specific module
uv run pytest tests/knowledge_graph/ -v

# Run the integration tests validating CLI behaviors
uv run pytest tests/test_scripts.py -v
```

## Structure

- **`analysis/`**: Validation of bibliometrics, NLP tokenization, and topic modeling logic.
- **`knowledge_graph/`**: Verification of RDF constructions, hypothesis bounds, and JSON parsing routines.
- **`literature/`**: `pytest-httpserver` proxies verifying multi-source paper extraction and canonical deduplication.
- **`visualization/`**: DataFrame consistency checks for all 16 plotting functions (using the headless backend).
- **`test_scripts.py`**: Integration tests confirming system calls and exit codes for the thin orchestrator `scripts/`.

See **[AGENTS.md](AGENTS.md)** for testing constraints, shared fixtures, and architectural guidelines.
