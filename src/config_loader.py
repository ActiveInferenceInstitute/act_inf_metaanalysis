"""YAML configuration loading for pipeline scripts."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from config import (
    DEFAULT_ARXIV_QUERIES,
    DEFAULT_COMPLETE_YEAR_POLICY,
    DEFAULT_N_TOPICS,
    DEFAULT_RELEVANCE_KEYWORDS,
    DEFAULT_SEED,
    DEFAULT_TOPIC_STABILITY_SEEDS,
    MANUSCRIPT_DIR,
    PIPELINE_VERSION,
    PROMPT_VERSION,
)


def _load_yaml(path: Path) -> dict[str, Any]:
    try:
        import yaml
    except ImportError:
        return {}
    if not path.exists():
        return {}
    with open(path, encoding="utf-8") as handle:
        data = yaml.safe_load(handle) or {}
    return data if isinstance(data, dict) else {}


def default_config_path() -> Path:
    """Return the canonical manuscript config path."""
    return MANUSCRIPT_DIR / "config.yaml"


def load_search_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load literature search settings from YAML."""
    data = _load_yaml(config_path or default_config_path())
    search_cfg = data.get("project_config", data).get("search", data.get("search", {}))
    cfg = {
        "query": search_cfg.get("query"),
        "max_results": search_cfg.get("max_results"),
        "resume": search_cfg.get("resume"),
        "clear_corpus": search_cfg.get("clear_corpus"),
        "arxiv_queries": search_cfg.get("arxiv_queries") or list(DEFAULT_ARXIV_QUERIES),
        "relevance_keywords": search_cfg.get("relevance_keywords")
        or list(DEFAULT_RELEVANCE_KEYWORDS),
        "start_year": search_cfg.get("start_year"),
        "semantic_scholar": search_cfg.get("semantic_scholar", {}) or {},
    }
    return cfg


def load_kg_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load knowledge-graph and LLM settings from YAML."""
    data = _load_yaml(config_path or default_config_path())
    project_cfg = data.get("project_config", {})
    kg_cfg = data.get("knowledge_graph", {}) or project_cfg.get("knowledge_graph", {})
    llm_cfg = data.get("llm_extraction", {}) or project_cfg.get("llm_extraction", {})
    return {
        "checkpoint_interval": kg_cfg.get("checkpoint_interval"),
        "clear_assertions": kg_cfg.get("clear_assertions"),
        "max_papers": kg_cfg.get("max_papers"),
        "llm_model": llm_cfg.get("model"),
        "llm_url": llm_cfg.get("base_url"),
        "worker_urls": tuple(llm_cfg.get("worker_urls") or ()),
        "llm_temperature": llm_cfg.get("temperature"),
        "llm_max_tokens": llm_cfg.get("max_tokens"),
        "llm_timeout": llm_cfg.get("timeout_seconds"),
        "llm_max_retries": llm_cfg.get("max_retries"),
        "llm_min_confidence": llm_cfg.get("min_confidence"),
        "pipeline_version": project_cfg.get("pipeline", {}).get(
            "pipeline_version", PIPELINE_VERSION
        ),
        "prompt_version": project_cfg.get("pipeline", {}).get(
            "prompt_version", PROMPT_VERSION
        ),
    }


def load_analysis_config(config_path: Path | None = None) -> dict[str, Any]:
    """Load reproducibility settings for the quantitative analysis stage."""
    data = _load_yaml(config_path or default_config_path())
    project_cfg = data.get("project_config", {})
    analysis_cfg = data.get("analysis", {}) or project_cfg.get("analysis", {})
    stability_seeds = analysis_cfg.get(
        "topic_stability_seeds", list(DEFAULT_TOPIC_STABILITY_SEEDS)
    )
    return {
        "n_topics": int(analysis_cfg.get("n_topics", DEFAULT_N_TOPICS)),
        "max_features": int(analysis_cfg.get("max_features", 500)),
        "min_year": int(analysis_cfg.get("min_year", 2000)),
        "seed": int(analysis_cfg.get("seed", DEFAULT_SEED)),
        "topic_stability_seeds": tuple(int(seed) for seed in stability_seeds),
        "complete_year_policy": analysis_cfg.get(
            "complete_year_policy", DEFAULT_COMPLETE_YEAR_POLICY
        ),
        "as_of_date": analysis_cfg.get("as_of_date"),
    }
