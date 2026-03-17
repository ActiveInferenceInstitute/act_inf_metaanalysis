# Knowledge Graph Module

Constructs and manages the RDF-compatible knowledge graph using the nanopublication model for the Active Inference Meta-Analysis.

## Components

- **Schema (`schema.py`)**: Custom `http://activeinference.institute/ontology/` definitions.
- **Hypothesis Scoring (`hypothesis.py`)**: Contains the 8 core hypotheses and evaluates citation-weighted evidence.
- **Nanopublication (`nanopublication.py`)**: Dataclasses and persistence for assertions.
- **Graph Builder (`graph_builder.py`)**: Main `KnowledgeGraph` manager (rdflib + networkx).
- **LLM Extraction (`llm_extraction.py`)**: Ollama-based agent for semantic evaluation of papers.
- **Query / Extraction (`query.py`, `extraction.py`)**: Graph querying helpers and assertion extraction logic.

See [AGENTS.md](AGENTS.md) for technical specifics.
