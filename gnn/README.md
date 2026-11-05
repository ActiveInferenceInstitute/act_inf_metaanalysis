# GNN Sketches of Hypothesis Structure

Three small [General Notation Notation][gnn] (GNN) models that make the
generative-model structure behind three of this project's hypotheses explicit
and machine-readable:

| File | Hypothesis | Code identifier | RDF URI |
| --- | --- | --- | --- |
| `h1_fep_universality.md` | `H1` | `FEP_UNIVERSALITY` | `http://activeinference.institute/ontology/H1_FEP_UNIVERSALITY` |
| `h4_predictive_coding.md` | `H4` | `PREDICTIVE_CODING` | `http://activeinference.institute/ontology/H4_PREDICTIVE_CODING` |
| `h8_language_aif.md` | `H8` | `LANGUAGE_AIF` | `http://activeinference.institute/ontology/H8_LANGUAGE_AIF` |

## What these files are, and what they are not

The hypotheses in `STANDARD_HYPOTHESES` are **claims**, and this project scores
them with citation-weighted evidence from the corpus. A claim about universality,
predictive coding, or language processing is a claim *about models*, and the
claim only means something once you say which model class it ranges over. These
sketches state that structure for three hypotheses, in a notation that parses
and type-checks.

They are **not** evidence, **not** results, and **not** inputs to any pipeline
stage:

- No pipeline orchestration, manifest, artifact contract, or manuscript variable
  reads this directory. The dedicated `scripts/validate_gnn_conformance.py`
  checker reads it only to parse and type-check the sketches in CI.
- The hypothesis scores, confidence intervals, temporal trends, and figures
  published by this project come only from the scored nanopublications
  (`output/data/assertion_summary.json`, `output/figures/`, `manuscript/`).
- Every parameter in every file is an **example value**. Uniform priors and
  round likelihoods were chosen on purpose so that no number can be mistaken for
  an estimate from the corpus.
- No data rule, claim rule, or terminology in `doc/hypotheses.md` changes
  because of these files.

Each file repeats this boundary in its own `ModelAnnotation` and `Footer`
sections, so the disclaimer travels with the model wherever it is copied.

## Why three, and why these three

The three sketches span three structurally different model classes, one per
hypothesis, which is enough to show what the notation makes explicit without
turning into a model zoo:

- **H1 (`FEP_UNIVERSALITY`)** — a boundary-maintaining system: a state that is
  either inside or outside bounds, a sensor that can detect deviation, and an
  action that restores the boundary. This is the minimal structure that
  "self-organizing system" language presupposes.
- **H4 (`PREDICTIVE_CODING`)** — prediction error minimization: a state that is
  either accounted for or not yet predicted, a sensor that reports match or
  mismatch, and a choice between updating the model and keeping it. The
  hierarchy of predictive coding (errors upward, predictions downward) is
  explicitly **not** represented; that limitation is stated in the file.
- **H8 (`LANGUAGE_AIF`)** — predictive language comprehension: two competing
  readings, a word form that fits one of them, and a choice between keeping the
  current reading and re-reading. The file states that the sketch takes no
  position on the explanatory-gain question that H8's contradicting evidence
  raises.

The remaining five hypotheses (`AIF_OPTIMALITY`, `MARKOV_BLANKET_REALISM`,
`SCALABILITY`, `CLINICAL_UTILITY`, `MORPHOGENESIS`) are not sketched here; the
set is deliberately bounded and can be extended one file at a time using the
same section layout.

## Worked example on the example parameters

Arithmetic on the example parameters above (no corpus data involved). For
`h1_fep_universality.md`, with `D = (0.7, 0.3)` and
`A = ((0.85, 0.10), (0.15, 0.90))`:

| Observation | Unnormalized `D[s] A[o,s]` | Posterior `q(s)` |
| --- | --- | --- |
| `o = 0` (no deviation sensed) | `(0.595, 0.030)` | `(0.9520, 0.0480)` |
| `o = 1` (deviation sensed) | `(0.105, 0.270)` | `(0.2800, 0.7200)` |

Feeding each posterior through `B[:,:,u]` gives the predicted next-state belief,
and the example transitions were chosen to make the point of the sketch visible:
the "restore" action lands on `(0.9, 0.1)` from either posterior, while "do
nothing" leaves a sensed deviation unresolved at `(0.34, 0.66)`. The same
computation for the other two sketches:

| File | Posterior after `o = 0` | Posterior after `o = 1` | Action 0 → next | Action 1 → next |
| --- | --- | --- | --- | --- |
| `h4_predictive_coding.md` (here `o = 1` is a mismatch) | `(0.8644, 0.1356)` | `(0.2195, 0.7805)` | `(0.8220, 0.1780)` | `(0.3317, 0.6683)` |
| `h8_language_aif.md` (here `o = 1` fits reading B) | `(0.7619, 0.2381)` | `(0.2105, 0.7895)` | `(0.3368, 0.6632)` | `(0.7132, 0.2868)` |

For H4 the row shows the choice the hypothesis is about: after a mismatch, "update
the model" moves the posterior to 82% accounted-for while "keep the model" leaves
it at 33%. For H8, "keep reading" preserves the B-dominant reading and "re-read"
moves belief toward the other reading.

## Verification

Parsed and type-checked with the real GNN pipeline (steps 3 and 5, no simulator
needed) at GNN revision `v5.0.3` (`8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`),
on 2026-11-01. The revision is exported into a scratch directory first, because a
live checkout can sit ahead of the pin:

```bash
# export exactly the pinned revision
git -C <gnn-checkout> archive 8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1 | tar -x -C /tmp/gnn-pin
# run steps 3 and 5 from that export, with the export's own sources first on the path
cd /tmp/gnn-pin
PYTHONPATH=/tmp/gnn-pin/src <gnn-python> src/gnn/main.py --only-steps 3,5 \
  --target-dir <this-directory> \
  --output-dir /tmp/gnn-metaanalysis-verify
```

`<gnn-python>` is any interpreter that has a GNN checkout's dependencies
installed (the checkout's own `.venv/bin/python` was used); the export's sources
win over any installed copy because `PYTHONPATH` takes precedence.

Observed: step 3 `SUCCESS`, 3 of 3 files parsed, 0 failures, 66 serialized
formats; step 5 `SUCCESS`, 3 of 3 files valid, 0 errors, 0 warnings; overall
`SUCCESS` in 6.6s. Recorded model digests:

| File | SHA-256 |
| --- | --- |
| `h1_fep_universality.md` | `6aee32e91bb055e97d518ba3aaafb99c703a87d83aa0be8ab2dba6b1fb3583d8` |
| `h4_predictive_coding.md` | `cfad9842cc4600e30d362d7b58ad9557b5d72f12a3de5cc75a734f09743b599d` |
| `h8_language_aif.md` | `e6ee2081007fd5324db0ff0b436678bb03473744bebd6d6208f31a50b42ce2d2` |

The digests are the ones the pipeline itself recorded for the consumed models,
so they can be re-checked with `shasum -a 256` on the files here.

This repository's own gate is unaffected and is still the thing to run for code
changes:

```bash
uv run pytest --cov=src --cov-fail-under=90 -v
```

See [AGENTS.md](AGENTS.md) for the constraints that apply when editing these
files.

## License

[CC-BY-4.0](../LICENSE), matching the repository.

[gnn]: https://github.com/ActiveInferenceInstitute/Generalized_Notation_Notation
