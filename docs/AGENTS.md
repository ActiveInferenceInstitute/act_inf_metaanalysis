# docs/ — documentation hub

`docs/` is the entry point for documentation in this repository.

## Contents

| File | Purpose |
| --- | --- |
| [`README.md`](README.md) | Hub: onboarding order, gate arms, pin facts, quick start |
| [`documentation-index.md`](documentation-index.md) | Flat index of every long-lived document |
| [`_generated/gate_arms.md`](_generated/gate_arms.md) | Measured wall time and evidence per gate arm |

The long-form guides (`architecture.md`, `scripts.md`, `testing.md`, and the
rest) live in [`../doc/`](../doc/); they were not moved because committed
pipeline manifests hash `doc/tooling_inventory.yaml`. [`../doc/AGENTS.md`](../doc/AGENTS.md)
holds the conventions for those guides.

## Rules

- Do not hand-edit `_generated/gate_arms.md`; run `./run.sh bench`.
- Keep links relative; `./run.sh docs` (`scripts/check_docs.py`) verifies every
  relative link, heading anchor, and the index coverage of `doc/`.
- New long-lived documents must appear in `documentation-index.md`.
