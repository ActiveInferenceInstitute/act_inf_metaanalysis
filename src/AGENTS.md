# Source Code Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/src/` directory.

## Overview

The `src/` directory contains all domain logic, classes, and functions required to execute the Active Inference computational meta-analysis. It adheres to the thin orchestrator pattern, ensuring that no business logic resides in the `scripts/` directory.

## Implementation Details

All code within `src/` is tested extensively (448 tests, 96.1% coverage) with zero mocks.

- It uses standard Python dataclasses for data modeling.
- All visualization code is segregated inside `visualization/`.
- All LLM interactions are decoupled from the core RDF model in `knowledge_graph/`.
- Uses deterministic RNG seeds (seed=42) to guarantee reproducible outputs.

Please refer to the specific `AGENTS.md` and `README.md` inside each subpackage for detailed capabilities.
