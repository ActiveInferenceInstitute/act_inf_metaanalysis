# `visualization.advanced`

Split implementation of the advanced figure functions. The public names are
re-exported by [`__init__.py`](__init__.py) and by the compatibility shim
[`../advanced_plots.py`](../advanced_plots.py), so callers keep importing from
`visualization.advanced_plots`.

## Modules

- [`labels.py`](labels.py) — `format_subfield_label` maps a subfield key to its
  display label via `SUBFIELD_NAMES` from [`../style.py`](../style.py).
- [`word_cloud.py`](word_cloud.py) — `plot_word_cloud` renders the TF-IDF term
  cloud (`wordcloud` is imported lazily, so it is only required when called).
- [`embeddings.py`](embeddings.py) — `plot_pca_embeddings`, `plot_term_heatmap`,
  and `plot_dendrogram` cover the PCA scatter, between-subfield-variance term
  heatmap, and Ward-linkage subfield dendrogram.
- [`topics.py`](topics.py) — `plot_topic_term_bars` and
  `plot_cooccurrence_matrix` cover the NMF topic panels and the normalized term
  co-occurrence heatmap.

All functions are called by [`../figure_runner.py`](../figure_runner.py) through
`scripts/04_generate_figures.py`. See [`../README.md`](../README.md) for the
figure-to-function map and [`AGENTS.md`](AGENTS.md) for editing constraints.
