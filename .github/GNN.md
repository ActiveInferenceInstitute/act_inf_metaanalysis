# GNN conformance

The conformance step runs in the workflow's single `gate` job (display name
`gate (lint, types, docs, gnn, tests)`). The step is named
`Pinned GNN conformance` and executes `./run.sh gnn`. It reads the canonical pin
file `.github/gnn-pin.json` (schema `gnn-importer-pin/v1`), which pins
`ActiveInferenceInstitute/Generalized_Notation_Notation` at tag `v5.0.3`,
revision `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`.

The job installs that pinned parser and parses and type-checks the repository's
three GNN sketches, `gnn/h1_fep_universality.md`,
`gnn/h4_predictive_coding.md` and `gnn/h8_language_aif.md`. Those sketches are
documentation, not pipeline input; this is a pipeline and pin conformance
record, not a claim that the repository contains a runnable generative model.

Run the same check locally with the gate arm:

```bash
./run.sh gnn
```

The arm is `scripts/gnn_conformance.py`. It creates `.gnn-env` for the pinned
revision, reuses it while the pin is unchanged, installs the parser with
`--no-deps` plus its declared runtime imports (`defusedxml`, `psutil`,
`pyyaml`), and then runs `scripts/validate_gnn_conformance.py`. The CI job runs
the same arm; the workflow does not use the
`ActiveInferenceInstitute/.github/.github/actions/setup-python-uv` composite
action, it pins `actions/checkout`, `actions/setup-python`, and
`astral-sh/setup-uv` directly.
