# Knowledge Graph Tests Architecture

**Archived test module** in the `projects_archive/act_inf_metaanalysis/tests/knowledge_graph/` directory.

## Overview

Tests within this directory target the central data schemas, LLM parsing utilities, and RDF semantic structures implemented in `src/knowledge_graph/`. Ensure that no actual LLM outbound requests are made during these tests; assertions must utilize pre-computed JSON mock strings matching Ollama output patterns to test the parsing logic directly.

## Key Validation Targets

- **`test_hypothesis.py`**: Ensures the 8 canonical hypotheses constrain values to exactly $[-1, 1]$ during the log-citation calculations. Verifies correct temporal cumulative evidence rollups.
- **`test_schema.py`**: Checks that the custom RDF namespace (`http://activeinference.institute/ontology/`) binds correctly and emits valid URI components.
- **`test_nanopublication.py`**: Validates the translation of an `Assertion` dataclass into an exact Nanopublication JSONL/RDF serialization block. Asserts correct unique UUID hashing.
- **`test_llm_extraction.py`**: Employs hard-coded multi-line Markdown strings containing JSON code-block fences to robustly verify the progressive JSON recovery parsing sequence (from pure JSON loads, to regex stripping, to element-wise error recovery) without requiring an active inference node.
- **`test_graph_builder.py`**: Uses simple 3-node dummy arrays to verify `rdflib` graph instantiation and edge generation.

See the directory `README.md` for execution instructions.
