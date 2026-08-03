# Manuscript Template Engine — Agent Directives

**Archived module** at `projects_archive/act_inf_metaanalysis/src/manuscript/`.

## Overview

Single module (`variables.py`) that reads all pipeline output JSONs and produces a complete
`dict[str, str]` of template variables. Called by `scripts/z_generate_manuscript_variables.py`.

## Invariants Agents Must Preserve

- **Always multiply by 100 for percentages**: `CAGR_PCT` = `cagr * 100`. The raw `cagr` from
  `temporal_analysis.json` is a decimal fraction (e.g., 0.1699 for 16.99%). Never output
  the fraction directly as CAGR_PCT — it would render as "0.17%" in the manuscript.
- **H1–H8 aliases are order-dependent**: The mapping H1 → `FEP_UNIVERSALITY`, ..., H8 →
  `LANGUAGE_AIF` must match the order of `STANDARD_HYPOTHESES` in `hypothesis.py`. If the
  hypothesis list order changes, update both files together.
- **Infrastructure fallback**: The try/except import of `get_logger` is intentional. Do not
  remove it — the module must work both inside the template monorepo and standalone.
- **Hydration is a gate**: `scripts/z_generate_manuscript_variables.py` performs the
  preflight check and fails when a source token has no computed value. Missing or stale
  artifacts must be repaired upstream rather than rendered as blank manuscript text.
- **LaTeX number formatting**: `_latex_number(n)` formats positive integers with `{,}` thousand
  separators for LaTeX (e.g., `2{,}795`). Negative numbers and floats are not handled — keep
  all counts non-negative.

## Adding a New Template Variable

1. Add a computation in `compute_variables()` reading from an existing JSON output file.
2. Store as a string: `variables["MY_VAR"] = f"{value}"`.
3. Place `{{MY_VAR}}` in the appropriate `manuscript/*.md` file.
4. Add a test in `tests/test_variables.py` verifying the value with a synthetic JSON file.
5. Update `README.md` variable table.

## Running Injection Manually

```bash
uv run python scripts/z_generate_manuscript_variables.py --project .
```

Output: `output/manuscript/*.md` — rendered copies of manuscript source files with all
uppercase `{{VAR}}` tokens replaced. The template engine recognizes the `z_` entrypoint
automatically and the stage also writes `output/data/manuscript_variables.json` with token
coverage and artifact hashes.

## Known Limitations

- **JSONL line counting**: `_count_jsonl_lines()` counts non-empty lines, not valid JSON objects.
  A malformed JSONL line counts as valid. For strict validation, use `deserialize_nanopubs()`.
- **Reference deduplication**: `_count_total_references()` sums per-paper reference lists
  without cross-paper deduplication. The total represents raw reference entries, not unique cited works.
