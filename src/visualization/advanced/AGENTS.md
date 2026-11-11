# Advanced Visualization Subpackage — Agent Directives

**Archived module** at `projects_archive/act_inf_metaanalysis/src/visualization/advanced/`.

## Overview

Implementation modules behind `visualization.advanced_plots`: label helpers
([`labels.py`](labels.py)), word cloud ([`word_cloud.py`](word_cloud.py)),
PCA/heatmap/dendrogram ([`embeddings.py`](embeddings.py)), and topic/co-occurrence
([`topics.py`](topics.py)). Public names are re-exported from
[`__init__.py`](__init__.py) and the sibling
[`../advanced_plots.py`](../advanced_plots.py) shim.

## Invariants

- **Agg backend**: `matplotlib.use("Agg")` must appear before `pyplot` in every
  module that imports matplotlib. Never import a display backend.
- **Fixed DPI**: save with `VIZ_CONFIG["dpi"]` (default 300); never hardcode a
  different DPI.
- **Colorblind palette**: use only `VIZ_CONFIG["palette"]` (Wong 2011, 8 colors)
  or a continuous colormap; do not extend the discrete palette.
- **Font floor**: no Matplotlib text below 16pt; use
  `max(VIZ_CONFIG["font_size"] - X, 16)`.
- **Discriminative term selection**: `plot_term_heatmap` ranks terms by
  between-subfield variance, not global mean TF-IDF. Do not revert that.
- **No side effects**: each function creates, saves, and closes its figure and
  returns the path; handle empty input without raising.
- **Lazy optional imports**: `wordcloud` (in `word_cloud.py`) and
  `sklearn`/`scipy` (in `embeddings.py`) are imported inside the functions so
  module import stays light.

## Adding a Function

1. Add it to the matching module with the signature
   `def plot_something(data: ..., output_path: Path, ...) -> Path`.
2. Call `plt.close(fig)` before returning and register the figure in
   `scripts/04_generate_figures.py`.
3. Add a `tests/visualization/` test using real numerical data and `tmp_path`.
4. Update this file and [`README.md`](README.md).

See [`../AGENTS.md`](../AGENTS.md) for the module-wide visualization rules.
