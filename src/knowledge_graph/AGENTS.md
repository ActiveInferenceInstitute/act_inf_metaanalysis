# Knowledge Graph Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/src/knowledge_graph/` directory.

## Overview

The core orchestration engine for evidence synthesis. It marries LLM-derived semantic assertions with graph-based ontological models to compute citation-weighted support for the 8 core hypotheses of Active Inference.

## Technical Details

- **RDF Compatibility**: Primarily relies on `rdflib` for robust graph operations but implements a graceful fallback to `networkx` to ensure resilience in constrained environments.
- **Nanopublications**: Represents each claim as a discrete, confidence-scored nanopublication, preserving provenance mapping from the `Paper` source.
- **LLM Decoupling**: The actual LLM prompting (via Ollama) is neatly abstracted in `llm_extraction.py`, providing incremental persistence guarantees (checkpoints) to recover quickly from interruptions without discarding progress.
