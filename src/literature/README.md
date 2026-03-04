# Literature Retrieval Module

Multi-source corpus generation for the Active Inference Meta-Analysis.

## Components

- **arXiv Client (`arxiv_client.py`)**: Interface for searching and parsing the arXiv Atom API.
- **Semantic Scholar (`semantic_scholar.py`)**: Client for the Semantic Scholar Graph API.
- **OpenAlex Client (`openalex_client.py`)**: Interface for querying the OpenAlex academic database.
- **Corpus Management (`corpus.py`)**: `Corpus` class handling serialization to JSONL and cross-source deduplication.
- **Models (`models.py`)**: Core data structures matching standard types: `Paper`, `Author`, and `Citation`.

See [AGENTS.md](AGENTS.md) for technical architecture details.
