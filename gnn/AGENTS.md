# GNN Sketches — Agent Guidance

Machine-readable context for `gnn/`, the directory that holds illustrative GNN
("Generalized Notation Notation") models of the generative-model structure that
three Standard Hypotheses presuppose.

## Purpose

Make the model structure behind a hypothesis explicit and machine-readable in a
notation that parses and type-checks, so a reader can see exactly what a claim
ranges over. One file per hypothesis, plus the `README.md` (human index) and
this file (agent context), following the repository's documentation duality
standard.

## Files

| File | Content |
| --- | --- |
| `README.md` | Human index: claim boundary, worked examples, verification receipts, license. |
| `AGENTS.md` | This file. |
| `h1_fep_universality.md` | Sketch for `H1` / `FEP_UNIVERSALITY`: boundary-maintaining system. |
| `h4_predictive_coding.md` | Sketch for `H4` / `PREDICTIVE_CODING`: prediction error minimization. |
| `h8_language_aif.md` | Sketch for `H8` / `LANGUAGE_AIF`: predictive language comprehension. |

## Hard constraints

1. **Never present a sketch as evidence.** These files carry no scores, no
   confidence intervals, no trends, and no numbers from the corpus. Every
   parameter is an example value; keep uniform or round values so nothing can be
   read as an estimate. The only sanctioned sources of evidence are the scored
   nanopublications and the generated outputs (`output/data/`,
   `output/figures/`, `manuscript/`).
2. **Never put a sketch in the pipeline.** Do not add `gnn/` to the pipeline
   orchestration, the artifact contract, the pipeline manifest, the release
   package, or any manuscript variable. The directory is documentation. The
   dedicated `scripts/validate_gnn_conformance.py` checker is the only script
   allowed to read it, and it only parses and type-checks the sketches.
3. **Never reorder or rename the hypotheses.** `STANDARD_HYPOTHESES` in
   `src/knowledge_graph/hypothesis.py` defines the `H1`–`H8` aliases across
   statements, weights, nanopublication targets, and manuscript variables. Cite
   the identifiers; do not change them or the set.
4. **Keep identifiers in sync with the source of truth.** When citing a
   hypothesis, use all three of its forms as they appear in
   `src/knowledge_graph/hypothesis.py` and `doc/hypotheses.md`: the config key
   (`H1`), the code identifier (`FEP_UNIVERSALITY`), and the RDF URI under
   `http://activeinference.institute/ontology/`. If the source changes, update
   the sketches and this file in the same change.
5. **State each sketch's limitations in the sketch itself.** Sections that
   collapse a hierarchy, omit a factor, or ignore an open dispute must say so in
   `ModelAnnotation`, next to the parameters they qualify.
6. **Keep the section layout.** Every sketch keeps the GNN section order used by
   the canonical exemplars (`GNNSection`, `GNNVersionAndFlags`, `ModelName`,
   `ModelAnnotation`, `StateSpaceBlock`, `Connections`, `InitialParameterization`,
   `Equations`, `Time`, `ActInfOntologyAnnotation`, `ModelParameters`, `Footer`,
   `Signature`); that is what makes them parseable by steps 3 and 5.
7. **No new dependencies, no vendored code.** The repository gains no GNN
   dependency from this directory; the sketches are plain Markdown.

## Verification

The repository gate is unchanged for code changes:

```bash
uv run pytest --cov=src --cov-fail-under=90 -v
```

The sketches themselves are verified by the `gnn conformance (pinned)` CI job.
It installs the revision in [`../.github/gnn-pin.json`](../.github/gnn-pin.json)
(v5.0.3, `8f293d9ba810e6eda5c09842d9c7ed9ffa5f92c1`), then runs
`python scripts/validate_gnn_conformance.py`; locally, use the same command in
an environment with the pinned GNN package installed. The script is strict: it
passes only when `GNNTypeChecker().validate_gnn_files` returns `True`. GNN's
pipeline contract is `0` = success, `1` = error, and `2` = success with
warnings; a `2` (type/consistency problems) or a `False` fails this gate and
exits non-zero. The receipt's `result` is `verified` only on that `True` path,
and `type-checker-result` records the value the checker actually returned. The
equivalent full pipeline check is:

```bash
python src/gnn/main.py --only-steps 3,5 \
  --target-dir <this-directory> \
  --output-dir /tmp/gnn-metaanalysis-verify
```

Expected: step 3 reports `successful_parses` equal to the number of sketches and
`failed_parses: 0`; step 5 reports `valid_files` equal to the number of sketches,
`total_errors: 0`, `total_warnings: 0`. Recompute the digests the pipeline
records for consumed models against `shasum -a 256` on the files here, and update
the table in `README.md` when a sketch changes. All three sketches were verified
this way on 2026-11-01.

## See also

- [README.md](README.md) — claim boundary and worked examples.
- [../doc/hypotheses.md](../doc/hypotheses.md) — hypothesis definitions and the
  scoring formula these sketches do not participate in.
- [../src/knowledge_graph/hypothesis.py](../src/knowledge_graph/hypothesis.py) —
  the authoritative hypothesis identifiers.
- [../doc/AGENTS.md](../doc/AGENTS.md) — documentation hub rules that also apply
  to this directory.
