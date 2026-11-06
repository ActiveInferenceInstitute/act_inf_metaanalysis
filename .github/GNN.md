# GNN conformance

`gnn conformance (pinned)` is defined in `.github/workflows/ci.yml` and reads
`.github/gnn-pin.json`, which pins
`ActiveInferenceInstitute/Generalized_Notation_Notation` at `v5.0.3`
(`8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`).

The job installs the pinned parser and parses and type-checks the repository's
three GNN sketches, `gnn/h1_fep_universality.md`,
`gnn/h4_predictive_coding.md` and `gnn/h8_language_aif.md`. Those sketches are
documentation, not pipeline input; this is a pipeline and pin conformance
record, not a claim that the repository contains a runnable generative model.
