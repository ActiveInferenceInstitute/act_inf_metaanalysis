# Documentation Hub Architecture

**This is an active module** in the `projects/act_inf_metaanalysis/doc/` directory.

## Overview

This directory (`doc/`) serves as the comprehensive, long-form technical documentation hub for the Active Inference Meta-Analysis project. It supplements the strictly localized `AGENTS.md` and `README.md` pair pattern found structurally inside every subdirectory of `src/` and `tests/` with generalized framework overviews appropriate for human researchers and developers.

## File Specifications

- `api_reference.md`: Granular documentation for all 45+ public APIs spread across the 5 source packages.
- `architecture.md`: Pipeline design, data-flow diagrams, and module dependency graphs mapping retrieval to visualization.
- `data_formats.md`: Strict JSONL, TriG, and Schema definitions governing Corpus storage and nanopublication validation.
- `hypotheses.md`: Domain theory constraints mapping the 8 core hypotheses to active inference literature.
- `scripts.md`: Detailed configuration and CLI flag mapping.
- `testing.md`: Explains the strict 534 unit-test zero-mock execution environment and philosophy.
- `visualization_guide.md`: Parameters for the 16 publication-ready generators.

Consult `README.md` within this directory for a complete index and pipeline stage mapping.
