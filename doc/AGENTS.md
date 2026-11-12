# Long-form guides (`doc/`)

Conventions for the long-form technical guides under `projects_archive/act_inf_metaanalysis/doc/`.
The documentation hub is [`../docs/README.md`](../docs/README.md) and the flat
index is [`../docs/documentation-index.md`](../docs/documentation-index.md).

## Overview

`doc/` holds the comprehensive, long-form technical guides for the Active
Inference Meta-Analysis project. It supplements the strictly localized
`AGENTS.md` and `README.md` pair pattern found inside every subdirectory of
`src/` and `tests/` with generalized framework overviews for researchers and
developers. Paths remain under `doc/` because committed pipeline manifests hash
`doc/tooling_inventory.yaml`.

## File Specifications

- `api_reference.md`: Granular documentation for the public APIs spread across the 5 source packages.
- `architecture.md`: Pipeline design, data-flow diagrams, and module dependency graphs mapping retrieval to visualization.
- `data_formats.md`: Strict JSONL, TriG, and Schema definitions governing Corpus storage and nanopublication validation.
- `citation_metadata.md`: `CITATION.cff`/DOI, per-paper citation fields, canonical-ID priority, and the citation-network artifacts.
- `hypotheses.md`: Domain theory constraints mapping the 8 core hypotheses to active inference literature.
- `scripts.md`: Detailed configuration and CLI flag mapping, including the render stage (`15_render_publication.py`).
- `testing.md`: Explains the strict zero-mock execution environment, the `slow`-marker fast/full split, and the coverage gate; measured counts live in `../docs/_generated/gate_arms.md`.
- `visualization_guide.md`: Parameters for the 16 publication-ready generators.
- `ai_meta_analysis_playbook.md`: Reproducible stage-by-stage operating procedure with recovery rules.
- `CODE_QUALITY_AUDIT.md`: Thermo-nuclear maintainability audit (2026-05-24) with 2026-07-31 addendum.
- `tooling_inventory.yaml`: Source registry for the publication-facing tooling table.
- `AGENTS.md`: This file.

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

Consult [`../docs/README.md`](../docs/README.md) for the hub and [`../docs/documentation-index.md`](../docs/documentation-index.md) for the flat index.
