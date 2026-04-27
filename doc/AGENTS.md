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
- `testing.md`: Explains the strict 553-test zero-mock execution environment and philosophy.
- `visualization_guide.md`: Parameters for the 16 publication-ready generators.
- `README.md`: Central index mapping the entire 5-stage pipeline and acting as the entrypoint.

## Agentic Directives (For AI Subagents)

If you are an AI subagent interacting with this repository, you **MUST** adhere to the following systemic constraints:

### 1. Document Duality Standard

Every source and test directory contains both an `AGENTS.md` (machine-readable architectural context) and a `README.md` (human-readable index). Whenever you add a new module or pipeline stage:

- You must update the respective `README.md` to reflect the new functionality.
- You must update the `AGENTS.md` to map its systemic purpose and constraints.

### 2. Zero-Mock Architecture Enforcement

The `tests/` directory operates under a strict **Zero-Mock Policy**.

- You are **never allowed to use `unittest.mock` or `monkeypatch`** to fake external endpoints (e.g. arXiv or Ollama).
- All external HTTP calls must be tested by injecting a `pytest-httpserver` base URL via the client's constructor.
- See `testing.md` for explicit examples of how to build compliant tests.

### 3. Visualization Accessibility Standards

When modifying or extending elements within `src/visualization/`:

- You are physically forbidden from rendering Matplotlib text smaller than **16pt**.
- All text additions (legends, annotations, labels) must explicitly calculate their size via `max(VIZ_CONFIG["font_size"] - X, 16)`.
- The Wong (2011) colorblind-safe palette defined in `style.py` must never be overridden.

Consult `README.md` within this directory for a complete index and pipeline stage mapping.
