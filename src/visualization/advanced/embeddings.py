"""PCA, heatmap, and dendrogram visualizations."""

from __future__ import annotations

import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from visualization.advanced.labels import format_subfield_label
from visualization.style import VIZ_CONFIG

logger = logging.getLogger(__name__)


def plot_pca_embeddings(
    tfidf_matrix: np.ndarray,
    labels: list[str],
    feature_names: list[str],
    output_path: Path,
    *,
    n_loading_arrows: int = 8,
) -> Path:
    from sklearn.decomposition import PCA

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(12, 9), dpi=VIZ_CONFIG["dpi"])
    if tfidf_matrix.shape[0] < 2 or tfidf_matrix.shape[1] < 2:
        ax.text(
            0.5,
            0.5,
            "Insufficient data for PCA",
            ha="center",
            va="center",
            fontsize=VIZ_CONFIG["font_size"],
        )
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    pca = PCA(n_components=2, random_state=42)
    coords = pca.fit_transform(tfidf_matrix)
    unique_labels = sorted(set(labels))
    subfield_colors = VIZ_CONFIG["subfield_colors"]
    palette = VIZ_CONFIG["palette"]
    for i, label in enumerate(unique_labels):
        mask = [lb == label for lb in labels]
        color = subfield_colors.get(label, palette[i % len(palette)])
        ax.scatter(
            coords[mask, 0],
            coords[mask, 1],
            c=color,
            label=format_subfield_label(label),
            alpha=0.65,
            s=40,
            edgecolors="white",
            linewidths=0.4,
        )

    if feature_names and n_loading_arrows > 0:
        loadings = pca.components_.T
        magnitude = np.sqrt(loadings[:, 0] ** 2 + loadings[:, 1] ** 2)
        top_idx = np.argsort(magnitude)[::-1][:n_loading_arrows]
        # Keep loading arrows inside the plotting region; scaling against 1.0
        # made sparse TF-IDF coordinates expand the canvas and push labels
        # far above the scatter panel.
        scale = max(float(abs(coords).max()), 0.3) * 0.45
        x_min, x_max = coords[:, 0].min(), coords[:, 0].max()
        y_min, y_max = coords[:, 1].min(), coords[:, 1].max()
        x_pad = max((x_max - x_min) * 0.08, 0.02)
        y_pad = max((y_max - y_min) * 0.08, 0.02)
        label_positions: list[tuple[float, float]] = []
        for idx in top_idx:
            dx, dy = loadings[idx] * scale
            label_x = float(np.clip(dx * 1.15, x_min + x_pad, x_max - x_pad))
            label_y = float(np.clip(dy * 1.15, y_min + y_pad, y_max - y_pad))
            # Text labels need more clearance than their anchor points. Use a
            # larger radial separation and a smaller publication-safe font so
            # nearby high-loading terms do not merge into an unreadable stack.
            min_separation = max(scale * 0.25, 0.08)
            while any(
                np.hypot(label_x - prev_x, label_y - prev_y) < min_separation
                for prev_x, prev_y in label_positions
            ):
                label_y = min(label_y + min_separation, y_max - y_pad)
                if any(
                    np.hypot(label_x - prev_x, label_y - prev_y) < min_separation
                    for prev_x, prev_y in label_positions
                ) and label_y >= y_max - y_pad:
                    label_x = max(label_x - min_separation, x_min + x_pad)
                    label_y = max(label_y - min_separation, y_min + y_pad)
            label_positions.append((label_x, label_y))
            ax.annotate(
                feature_names[idx],
                xy=(dx, dy),
                fontsize=max(VIZ_CONFIG["font_size"] - 6, 12),
                alpha=0.7,
                ha="left" if label_x >= 0 else "right",
                arrowprops=dict(arrowstyle="<-", color="gray", lw=0.8),
                xytext=(label_x, label_y),
            )

    var1, var2 = pca.explained_variance_ratio_ * 100
    ax.set_xlabel(f"PC1 ({var1:.1f}% variance)", fontsize=VIZ_CONFIG["font_size"])
    ax.set_ylabel(f"PC2 ({var2:.1f}% variance)", fontsize=VIZ_CONFIG["font_size"])
    ax.set_title(
        "PCA of TF-IDF Document Embeddings",
        fontsize=VIZ_CONFIG["title_size"],
        fontweight="bold",
    )
    ax.legend(fontsize=max(VIZ_CONFIG["font_size"] - 2, 16), loc="best", ncol=2)
    ax.grid(alpha=VIZ_CONFIG["grid_alpha"])
    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    return output_path


def plot_term_heatmap(
    tfidf_matrix: np.ndarray,
    feature_names: list[str],
    labels: list[str],
    output_path: Path,
    *,
    n_terms: int = 20,
) -> Path:
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(14, 8), dpi=VIZ_CONFIG["dpi"])
    if tfidf_matrix.size == 0 or not labels:
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    unique_labels = sorted(set(labels))
    label_arr = np.array(labels)
    means = np.zeros((len(unique_labels), tfidf_matrix.shape[1]))
    for i, lab in enumerate(unique_labels):
        mask = label_arr == lab
        if mask.any():
            means[i] = tfidf_matrix[mask].mean(axis=0)

    between_group_variance = means.var(axis=0)
    top_idx = np.argsort(between_group_variance)[::-1][:n_terms]
    heatmap_data = means[:, top_idx]
    term_labels = [feature_names[j] for j in top_idx]
    im = ax.imshow(heatmap_data, aspect="auto", cmap="YlOrRd", interpolation="nearest")
    ax.set_xticks(range(len(term_labels)))
    ax.set_xticklabels(
        term_labels,
        rotation=45,
        ha="right",
        fontsize=max(VIZ_CONFIG["font_size"] - 2, 16),
    )
    ax.set_yticks(range(len(unique_labels)))
    ax.set_yticklabels(
        [format_subfield_label(label) for label in unique_labels],
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
    return output_path


def plot_dendrogram(
    tfidf_matrix: np.ndarray,
    labels: list[str],
    output_path: Path,
) -> Path:
    from scipy.cluster.hierarchy import cophenet, dendrogram as scipy_dendrogram, linkage
    from scipy.spatial.distance import pdist

    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(10, 7), dpi=VIZ_CONFIG["dpi"])
    unique_labels = sorted(set(labels))
    if len(unique_labels) < 2:
        ax.set_axis_off()
        fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
        plt.close(fig)
        return output_path

    label_arr = np.array(labels)
    centroids = np.array(
        [tfidf_matrix[label_arr == lab].mean(axis=0) for lab in unique_labels]
    )
    z_link = linkage(centroids, method="ward")
    scipy_dendrogram(
        z_link,
        labels=[format_subfield_label(label) for label in unique_labels],
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
    coph_corr, _ = cophenet(z_link, pdist(centroids))
    ax.text(
        0.98,
        0.96,
        f"Cophenetic r = {coph_corr:.2f}",
        transform=ax.transAxes,
        ha="right",
        va="top",
        fontsize=max(VIZ_CONFIG["font_size"] - 2, 16),
        bbox=dict(boxstyle="round,pad=0.3", fc="white", alpha=0.8),
    )
    plt.tight_layout()
    fig.savefig(output_path, dpi=VIZ_CONFIG["dpi"], bbox_inches="tight")
    plt.close(fig)
    return output_path
