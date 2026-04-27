"""Advanced visualizations for Active Inference meta-analysis.

Provides word clouds, PCA embedding scatter plots, term heatmaps,
hierarchical clustering dendrograms, topic-term bar charts, and
term co-occurrence matrices.  All functions follow the same API
pattern: accept data + output_path, return the saved path.
"""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from visualization.style import VIZ_CONFIG, SUBFIELD_NAMES

logger = logging.getLogger(__name__)


def _format_subfield_label(sf: str) -> str:
    """Standardize subfield label using SUBFIELD_NAMES."""
    return SUBFIELD_NAMES.get(sf, sf.replace("_", " ").title())


# ---------------------------------------------------------------------------
# 1. Word Cloud
# ---------------------------------------------------------------------------

def plot_word_cloud(
    word_weights: dict[str, float],
    output_path: Path,
    *,
    max_words: int = 100,
) -> Path:
    """Generate a word cloud from term weights.

    Args:
        word_weights: Mapping of term to weight (e.g. mean TF-IDF).
        output_path: File path to save the figure.
        max_words: Maximum number of words in the cloud.

    Returns:
        The output_path after saving.
    """
    from wordcloud import WordCloud

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 8), dpi=VIZ_CONFIG["dpi"])

    if not word_weights:
        ax.text(0.5, 0.5, "No word data available",
                ha="center", va="center", fontsize=VIZ_CONFIG["font_size"])
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    wc = WordCloud(
        width=1200,
        height=800,
        max_words=max_words,
        background_color="white",
        colormap="cividis",
        prefer_horizontal=0.7,
        min_font_size=16,
    ).generate_from_frequencies(word_weights)

    ax.imshow(wc, interpolation="bilinear")
    ax.set_axis_off()
    ax.set_title(
        "Active Inference Literature — Term Cloud",
        fontsize=VIZ_CONFIG["title_size"],
        fontweight="bold",
        pad=12,
    )

    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    logger.info("📊 Word cloud saved: %s (%d terms)", output_path, len(word_weights))
    return output_path


# ---------------------------------------------------------------------------
# 2. PCA Embedding Scatter
# ---------------------------------------------------------------------------

def plot_pca_embeddings(
    tfidf_matrix: np.ndarray,
    labels: list[str],
    feature_names: list[str],
    output_path: Path,
    *,
    n_loading_arrows: int = 8,
) -> Path:
    """2-D PCA scatter of documents colored by subfield label.

    Optionally overlays loading arrows for the highest-variance terms.

    Args:
        tfidf_matrix: TF-IDF matrix of shape (n_docs, n_features).
        labels: Per-document subfield label (same length as rows).
        feature_names: Feature names for loading arrows.
        output_path: File path to save the figure.
        n_loading_arrows: Number of top-loading terms to annotate.

    Returns:
        The output_path after saving.
    """
    from sklearn.decomposition import PCA

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 9), dpi=VIZ_CONFIG["dpi"])

    if tfidf_matrix.shape[0] < 2 or tfidf_matrix.shape[1] < 2:
        ax.text(0.5, 0.5, "Insufficient data for PCA",
                ha="center", va="center", fontsize=VIZ_CONFIG["font_size"])
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf_matrix)

    # Group by label and color
    unique_labels = sorted(set(labels))
    subfield_colors = VIZ_CONFIG["subfield_colors"]
    palette = VIZ_CONFIG["palette"]

    for i, label in enumerate(unique_labels):
        mask = [lb == label for lb in labels]
        color = subfield_colors.get(label, palette[i % len(palette)])
        ax.scatter(
            coords[mask, 0], coords[mask, 1],
            c=color, label=_format_subfield_label(label),
            alpha=0.65, s=40, edgecolors="white", linewidths=0.4,
        )

    # Loading arrows
    if feature_names and n_loading_arrows > 0:
        loadings = pca.components_.T  # (n_features, 2)
        magnitude = np.sqrt(loadings[:, 0] ** 2 + loadings[:, 1] ** 2)
        top_idx = np.argsort(magnitude)[::-1][:n_loading_arrows]
        scale = max(abs(coords).max(), 1.0) * 0.7
        for idx in top_idx:
            dx, dy = loadings[idx] * scale
            ax.annotate(
                feature_names[idx],
                xy=(dx, dy),
                fontsize=max(VIZ_CONFIG["font_size"] - 3, 16),
                alpha=0.7,
                ha="center",
                arrowprops=dict(arrowstyle="<-", color="gray", lw=0.8),
                xytext=(dx * 1.15, dy * 1.15),
            )

    var1, var2 = pca.explained_variance_ratio_ * 100
    total_var = var1 + var2
    ax.set_xlabel(f"PC1 ({var1:.1f}% variance)", fontsize=VIZ_CONFIG["font_size"])
    ax.set_ylabel(f"PC2 ({var2:.1f}% variance)", fontsize=VIZ_CONFIG["font_size"])
    ax.set_title(
        "PCA of TF-IDF Document Embeddings",
        fontsize=VIZ_CONFIG["title_size"],
        fontweight="bold",
    )
    ax.text(
        0.5, 1.01, f"Total variance explained: {total_var:.1f}%",
        transform=ax.transAxes, ha="center",
        fontsize=max(VIZ_CONFIG["font_size"] - 2, 16), color="gray",
    )
    ax.legend(fontsize=max(VIZ_CONFIG["font_size"] - 2, 16), loc="best",
              framealpha=0.9, ncol=2)
    ax.grid(alpha=VIZ_CONFIG["grid_alpha"])

    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    logger.info("📊 PCA embeddings saved: %s (%d docs)", output_path, tfidf_matrix.shape[0])
    return output_path


# ---------------------------------------------------------------------------
# 3. Term × Subfield Heatmap
# ---------------------------------------------------------------------------

def plot_term_heatmap(
    tfidf_matrix: np.ndarray,
    feature_names: list[str],
    labels: list[str],
    output_path: Path,
    *,
    n_terms: int = 20,
) -> Path:
    """Heatmap of mean TF-IDF weight for top terms across subfields.

    Args:
        tfidf_matrix: TF-IDF matrix (n_docs, n_features).
        feature_names: Vocabulary terms.
        labels: Per-document subfield label.
        output_path: File path to save the figure.
        n_terms: Number of top terms to display.

    Returns:
        The output_path after saving.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(14, 8), dpi=VIZ_CONFIG["dpi"])

    if tfidf_matrix.size == 0 or not labels:
        ax.text(0.5, 0.5, "No data available",
                ha="center", va="center", fontsize=VIZ_CONFIG["font_size"])
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    unique_labels = sorted(set(labels))
    label_arr = np.array(labels)

    # Mean TF-IDF per subfield per term
    means = np.zeros((len(unique_labels), tfidf_matrix.shape[1]))
    for i, lab in enumerate(unique_labels):
        mask = label_arr == lab
        if mask.any():
            means[i] = tfidf_matrix[mask].mean(axis=0)

    # Select top n_terms by between-subfield variance, not global mean.
    # Variance across subfield centroids identifies discriminative terms
    # that differentiate domains; global-mean selection instead favours
    # ubiquitous terms (e.g. "inference") that appear everywhere equally.
    between_group_variance = means.var(axis=0)
    top_idx = np.argsort(between_group_variance)[::-1][:n_terms]
    heatmap_data = means[:, top_idx]
    term_labels = [feature_names[j] for j in top_idx]

    im = ax.imshow(heatmap_data, aspect="auto", cmap="YlOrRd", interpolation="nearest")

    ax.set_xticks(range(len(term_labels)))
    ax.set_xticklabels(term_labels, rotation=45, ha="right",
                       fontsize=max(VIZ_CONFIG["font_size"] - 2, 16))
    ax.set_yticks(range(len(unique_labels)))
    ax.set_yticklabels(
        [_format_subfield_label(l) for l in unique_labels],
        fontsize=max(VIZ_CONFIG["font_size"] - 1, 16),
    )
    ax.set_title(
        "Term × Subfield Heatmap (Mean TF-IDF)",
        fontsize=VIZ_CONFIG["title_size"],
        fontweight="bold",
    )
    fig.colorbar(im, ax=ax, label="Mean TF-IDF Weight", shrink=0.8)

    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    logger.info("📊 Term heatmap saved: %s (%d terms × %d subfields)",
                output_path, n_terms, len(unique_labels))
    return output_path


# ---------------------------------------------------------------------------
# 4. Hierarchical Clustering Dendrogram
# ---------------------------------------------------------------------------

def plot_dendrogram(
    tfidf_matrix: np.ndarray,
    labels: list[str],
    output_path: Path,
) -> Path:
    """Dendrogram of hierarchical clustering on subfield mean TF-IDF vectors.

    Uses Ward linkage on the subfield centroids to show semantic proximity
    between research areas.

    Args:
        tfidf_matrix: TF-IDF matrix (n_docs, n_features).
        labels: Per-document subfield label.
        output_path: File path to save the figure.

    Returns:
        The output_path after saving.
    """
    from scipy.cluster.hierarchy import linkage, dendrogram as scipy_dendrogram

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(10, 7), dpi=VIZ_CONFIG["dpi"])

    unique_labels = sorted(set(labels))
    if len(unique_labels) < 2:
        ax.text(0.5, 0.5, "Need ≥2 subfields for dendrogram",
                ha="center", va="center", fontsize=VIZ_CONFIG["font_size"])
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    label_arr = np.array(labels)
    centroids = []
    for lab in unique_labels:
        mask = label_arr == lab
        centroids.append(tfidf_matrix[mask].mean(axis=0))

    centroids = np.array(centroids)

    Z = linkage(centroids, method="ward")

    scipy_dendrogram(
        Z,
        labels=[_format_subfield_label(l) for l in unique_labels],
        leaf_rotation=30,
        leaf_font_size=VIZ_CONFIG["font_size"],
        ax=ax,
        color_threshold=0,
        above_threshold_color=VIZ_CONFIG["palette"][0],
    )
    ax.set_title(
        "Subfield Hierarchical Clustering (Ward Linkage)",
        fontsize=VIZ_CONFIG["title_size"],
        fontweight="bold",
    )
    ax.set_ylabel("Ward Distance", fontsize=VIZ_CONFIG["font_size"])
    ax.grid(axis="y", alpha=VIZ_CONFIG["grid_alpha"])

    # Annotate cophenetic correlation
    from scipy.cluster.hierarchy import cophenet
    from scipy.spatial.distance import pdist
    coph_corr, _ = cophenet(Z, pdist(centroids))
    ax.text(
        0.98, 0.96, f"Cophenetic r = {coph_corr:.2f}",
        transform=ax.transAxes, ha="right", va="top",
        fontsize=max(VIZ_CONFIG["font_size"] - 2, 16),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),
    )

    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    logger.info("📊 Dendrogram saved: %s (%d subfields)", output_path, len(unique_labels))
    return output_path


# ---------------------------------------------------------------------------
# 5. Topic-Term Bar Charts
# ---------------------------------------------------------------------------

def plot_topic_term_bars(
    topics: list[dict],
    output_path: Path,
) -> Path:
    """Faceted horizontal bar charts showing top terms per NMF topic.

    Args:
        topics: List of topic dicts, each with keys
            'topic_id', 'top_words', 'weights'.
        output_path: File path to save the figure.

    Returns:
        The output_path after saving.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    n_topics = len(topics)
    if n_topics == 0:
        fig, ax = plt.subplots(figsize=VIZ_CONFIG["figure_size"], dpi=VIZ_CONFIG["dpi"])
        ax.text(0.5, 0.5, "No topics available",
                ha="center", va="center", fontsize=VIZ_CONFIG["font_size"])
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    ncols = min(n_topics, 3)
    nrows = (n_topics + ncols - 1) // ncols
    fig, axes = plt.subplots(nrows, ncols, figsize=(6 * ncols, 4 * nrows),
                             dpi=VIZ_CONFIG["dpi"])
    if n_topics == 1:
        axes = np.array([axes])
    axes = np.atleast_2d(axes)

    palette = VIZ_CONFIG["palette"]

    for idx, topic in enumerate(topics):
        row, col = divmod(idx, ncols)
        ax = axes[row, col]

        words = topic.get("top_words", [])[:10]
        weights = topic.get("weights", [])[:10]

        if not words:
            ax.set_axis_off()
            continue

        # Reverse for horizontal bars (bottom to top)
        words = words[::-1]
        weights = weights[::-1]

        color = palette[idx % len(palette)]
        ax.barh(range(len(words)), weights, color=color, edgecolor="white", linewidth=0.3)
        ax.set_yticks(range(len(words)))
        ax.set_yticklabels(words, fontsize=max(VIZ_CONFIG["font_size"] - 2, 16))
        ax.set_title(f"Topic {topic.get('topic_id', idx)}",
                     fontsize=VIZ_CONFIG["font_size"], fontweight="bold")
        ax.grid(axis="x", alpha=VIZ_CONFIG["grid_alpha"])

    # Hide unused subplots
    for idx in range(n_topics, nrows * ncols):
        row, col = divmod(idx, ncols)
        axes[row, col].set_axis_off()

    fig.suptitle(
        "NMF Topic — Top Terms",
        fontsize=VIZ_CONFIG["title_size"],
        fontweight="bold",
        y=1.02,
    )

    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    logger.info("📊 Topic-term bars saved: %s (%d topics)", output_path, n_topics)
    return output_path


# ---------------------------------------------------------------------------
# 6. Term Co-occurrence Matrix
# ---------------------------------------------------------------------------

def plot_cooccurrence_matrix(
    documents: list[list[str]],
    output_path: Path,
    *,
    n_terms: int = 30,
) -> Path:
    """Heatmap of term co-occurrence across documents.

    Counts how often pairs of top terms appear together in the same
    document and visualizes as a symmetric heatmap.

    Args:
        documents: List of token lists (one per document).
        output_path: File path to save the figure.
        n_terms: Number of most-frequent terms to include.

    Returns:
        The output_path after saving.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    fig, ax = plt.subplots(figsize=(12, 10), dpi=VIZ_CONFIG["dpi"])

    if not documents:
        ax.text(0.5, 0.5, "No co-occurrence data",
                ha="center", va="center", fontsize=VIZ_CONFIG["font_size"])
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    # Count term frequency across documents
    term_doc_freq: dict[str, int] = {}
    for tokens in documents:
        unique_tokens = set(tokens)
        for t in unique_tokens:
            term_doc_freq[t] = term_doc_freq.get(t, 0) + 1

    # Top n terms by doc frequency
    sorted_terms = sorted(term_doc_freq.keys(), key=lambda t: -term_doc_freq[t])
    top_terms = sorted_terms[:n_terms]
    term_idx = {t: i for i, t in enumerate(top_terms)}
    n = len(top_terms)

    if n < 2:
        ax.text(0.5, 0.5, "Insufficient terms for co-occurrence",
                ha="center", va="center", fontsize=VIZ_CONFIG["font_size"])
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    cooc = np.zeros((n, n), dtype=np.float64)
    for tokens in documents:
        present = [t for t in set(tokens) if t in term_idx]
        for i_term in range(len(present)):
            for j_term in range(i_term + 1, len(present)):
                a, b = term_idx[present[i_term]], term_idx[present[j_term]]
                cooc[a, b] += 1
                cooc[b, a] += 1

    # Normalize to [0, 1], zeroing diagonal (trivial self-co-occurrence)
    np.fill_diagonal(cooc, 0.0)
    max_val = cooc.max()
    if max_val > 0:
        cooc /= max_val

    im = ax.imshow(cooc, cmap="Blues", interpolation="nearest", vmin=0, vmax=1)
    ax.set_xticks(range(n))
    ax.set_xticklabels(top_terms, rotation=45, ha="right",
                       fontsize=max(VIZ_CONFIG["font_size"] - 3, 16))
    ax.set_yticks(range(n))
    ax.set_yticklabels(top_terms,
                       fontsize=max(VIZ_CONFIG["font_size"] - 3, 16))
    ax.set_title(
        "Term Co-occurrence Matrix",
        fontsize=VIZ_CONFIG["title_size"],
        fontweight="bold",
    )
    fig.colorbar(im, ax=ax, label="Normalized Co-occurrence", shrink=0.8)

    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    logger.info("📊 Co-occurrence matrix saved: %s (%d terms)", output_path, n)
    return output_path
