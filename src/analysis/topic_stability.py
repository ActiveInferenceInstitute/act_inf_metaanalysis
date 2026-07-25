"""Deterministic NMF topic stability diagnostics."""

from __future__ import annotations

from itertools import permutations

import numpy as np

from analysis.topic_modeling import fit_nmf_topics


def _best_mean_jaccard(left: list[set[str]], right: list[set[str]]) -> float:
    """Match topic labels across runs and return the best mean Jaccard score."""
    n_topics = min(len(left), len(right))
    if n_topics == 0:
        return 0.0
    matrix = np.zeros((n_topics, n_topics), dtype=float)
    for i, left_terms in enumerate(left[:n_topics]):
        for j, right_terms in enumerate(right[:n_topics]):
            union = left_terms | right_terms
            matrix[i, j] = (
                len(left_terms & right_terms) / len(union) if union else 1.0
            )

    if n_topics <= 8:
        return max(
            sum(matrix[i, permutation[i]] for i in range(n_topics)) / n_topics
            for permutation in permutations(range(n_topics))
        )

    used: set[int] = set()
    values: list[float] = []
    for row in matrix:
        candidates = sorted(
            ((value, column) for column, value in enumerate(row) if column not in used),
            reverse=True,
        )
        if candidates:
            value, column = candidates[0]
            used.add(column)
            values.append(float(value))
    return sum(values) / len(values) if values else 0.0


def compute_topic_stability(
    tfidf_matrix: np.ndarray,
    feature_names: list[str],
    *,
    n_topics: int,
    seeds: tuple[int, ...] | list[int],
) -> dict:
    """Compare top-term topic sets over a fixed set of NMF seeds."""
    seed_list = list(dict.fromkeys(int(seed) for seed in seeds))
    runs = {
        seed: fit_nmf_topics(
            tfidf_matrix,
            feature_names,
            n_topics=n_topics,
            seed=seed,
        )
        for seed in seed_list
    }
    pairwise: list[dict[str, float | int]] = []
    for index, left_seed in enumerate(seed_list):
        for right_seed in seed_list[index + 1 :]:
            left_topics = [set(topic["top_words"]) for topic in runs[left_seed]]
            right_topics = [set(topic["top_words"]) for topic in runs[right_seed]]
            pairwise.append(
                {
                    "seed_a": left_seed,
                    "seed_b": right_seed,
                    "mean_jaccard": _best_mean_jaccard(left_topics, right_topics),
                }
            )
    values = [float(item["mean_jaccard"]) for item in pairwise]
    return {
        "n_topics": n_topics,
        "seeds": seed_list,
        "primary_seed": 42 if 42 in seed_list else (seed_list[0] if seed_list else None),
        "pairwise_comparisons": pairwise,
        "mean_jaccard": sum(values) / len(values) if values else 1.0,
        "min_jaccard": min(values) if values else 1.0,
    }


__all__ = ["compute_topic_stability"]
