# Knowledge Graph Module — Agent Directives

**Archived module** at `projects_archive/act_inf_metaanalysis/src/knowledge_graph/`.

## Overview

The core evidence synthesis layer. Orchestration: `knowledge_graph/kg_runner.py`
(`scripts/03_build_knowledge_graph.py`). The LLM extraction sub-system is the most expensive
operation in the pipeline — use incremental mode (the default) whenever possible.

## Invariants Agents Must Preserve

- **Incremental extraction**: `llm_extraction.py` skips papers already in `nanopublications.jsonl`.
  Never delete this file without the `--clear-assertions` flag unless explicitly asked to restart.
  Deleting it triggers full LLM re-extraction (~hours on local Ollama).
- **Confidence floor**: `min_confidence: 0.6` is the validated extraction threshold (the default in `LLMConfig`). Do not lower it without re-running the calibration study. Note: the real agreement figures are κ=0.704 for *rule-vs-rule* stability of the reference protocols; the pipeline-vs-rule-reference κ is −0.048, so the 0.6 gate is a pipeline-design constant, not a calibrated human-agreement milestone.
- **RDF namespace stability**: `AIF_NAMESPACE = "http://activeinference.institute/ontology/"` is
  published in the nanopub.trig output. Never change it without a migration script that rewrites
  all existing nanopublications.
- **Score range**: `score_hypothesis()` returns a value in [−1, +1]. A return of `0.0` is
  ambiguous (no assertions OR balanced evidence). Always check assertion counts.
- **Hypothesis ID order**: `STANDARD_HYPOTHESES` list order determines H1–H8 aliases in
  `variables.py`. Do not reorder without updating the alias mapping.
- **No mock policy**: Tests must use real `Assertion` objects and real score computations.

## LLM Extraction Workflow

```bash
# Incremental (default) — skips already-processed papers
uv run python scripts/03_build_knowledge_graph.py --config manuscript/config.yaml

# Full re-extraction (WARNING: overwrites existing assertions in nanopublications.jsonl)
uv run python scripts/03_build_knowledge_graph.py --clear-assertions

# Score-only mode — reload from existing nanopubs, no LLM calls
uv run python scripts/03_build_knowledge_graph.py --max-papers 0
```

Ollama must be running at the configured `project_config.llm_extraction.base_url`
with the configured model pulled. The current publication config uses `gemma3:4b`.

## RDF Graph Structure (per nanopublication)

```
<base>/<id>#head       — links nanopub to its three component graphs
<base>/<id>#assertion  — the claim: paper aif:asserts assertion; assertion aif:supports hypothesis
<base>/<id>#provenance — prov:wasGeneratedBy, prov:generatedAtTime, prov:wasAttributedTo
<base>/<id>#pubinfo    — dc:created, dc:creator, dc:license
```

## Adding a New Hypothesis

1. Add a `Hypothesis` object to `STANDARD_HYPOTHESES` in `hypothesis.py`.
2. Add the corresponding URI to `HYPOTHESIS_CATEGORIES` in `schema.py`.
3. Add the H-alias mapping (`"H9"` → new ID) in `src/manuscript/variables.py`.
4. Add keyword definitions in `manuscript/config.yaml` under `hypotheses:`.
5. Regenerate nanopublications via `--clear-assertions` (new hypothesis won't have assertions otherwise).
6. Update `manuscript/03_results_hypothesis.md` with a new row in the evidence table.

## Known Limitations

- **Abstract-only extraction**: LLM sees only title + abstract, not full text. Claims in
  methods/results sections are missed. See manuscript Step 2 (full-text extraction) roadmap.
- **Abstract-only extraction**: The extractor is intentionally limited to title and abstract
  evidence; full-text availability is assessed separately and does not imply extraction.
- **Assertion ID collision**: IDs use `f"llm_{paper_id}_{hypothesis_id}"`. Reprocessing the
  same paper creates a duplicate that `merge_nanopubs` deduplicates by overwrite.
