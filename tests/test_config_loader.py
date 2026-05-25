"""Tests for config_loader."""

from __future__ import annotations

from pathlib import Path

from config import DEFAULT_ARXIV_QUERIES, DEFAULT_RELEVANCE_KEYWORDS
from config_loader import load_kg_config, load_search_config


def test_load_search_config_defaults_when_missing(tmp_path: Path) -> None:
    cfg = load_search_config(tmp_path / "missing.yaml")
    assert cfg["arxiv_queries"] == DEFAULT_ARXIV_QUERIES
    assert cfg["relevance_keywords"] == DEFAULT_RELEVANCE_KEYWORDS


def test_load_kg_config_empty_when_missing(tmp_path: Path) -> None:
    cfg = load_kg_config(tmp_path / "missing.yaml")
    assert cfg.get("checkpoint_interval") is None
