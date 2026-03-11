#!/usr/bin/env python3
"""Knowledge graph construction orchestrator.

Thin orchestrator that loads a corpus, constructs a knowledge graph
with nanopublication assertions, scores hypotheses, and persists
results. All computation is imported from src/ modules.

**Incremental by default:** The LLM extraction layer persists
assertions directly to ``nanopublications.jsonl`` at regular intervals
via :func:`~knowledge_graph.nanopublication.append_nanopubs`.  On
restart, already-persisted papers are skipped automatically — there
is no separate checkpoint file.  Use ``--clear-assertions`` to
discard previous results and start fresh.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

# Add src/ to path for project imports
ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "src"
sys.path.insert(0, str(SRC))

from literature.corpus import Corpus
from literature.models import Paper
from knowledge_graph.schema import HYPOTHESIS_CATEGORIES
from knowledge_graph.nanopublication import (
    Assertion,
    deserialize_nanopubs,
    get_processed_paper_ids,
    serialize_nanopubs_to_trig,
)
from knowledge_graph.extraction import extract_assertions
from knowledge_graph.llm_extraction import LLMConfig
from knowledge_graph.hypothesis import (
    STANDARD_HYPOTHESES,
    HYPOTHESES,
    score_all_hypotheses,
    temporal_trend,
    configure_hypotheses,
)


def _load_kg_config(config_path: Path) -> dict:
    """Load knowledge_graph configuration from a YAML file.

    Args:
        config_path: Path to the YAML configuration file.

    Returns:
        Dictionary with KG-related config keys.
    """
    try:
        import yaml
    except ImportError:
        return {}
    with open(config_path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f) or {}
    kg_cfg = data.get("knowledge_graph", {})
    return {
        "checkpoint_interval": kg_cfg.get("checkpoint_interval"),
        "clear_assertions": kg_cfg.get("clear_assertions"),
        "max_papers": kg_cfg.get("max_papers"),
    }

def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Build knowledge graph and score hypotheses."
    )
    parser.add_argument(
        "--corpus",
        type=str,
        default=str(ROOT / "output" / "data" / "corpus.jsonl"),
        help="Path to corpus JSONL file",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default=str(ROOT / "output"),
        help="Output directory for KG results",
    )
    parser.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging verbosity (default: INFO)",
    )
    parser.add_argument(
        "--llm-model",
        type=str,
        default="gemma3:4b",
        help="Ollama model name for LLM extraction (default: gemma3:4b)",
    )
    parser.add_argument(
        "--llm-url",
        type=str,
        default="http://localhost:11434",
        help="Ollama API base URL (default: http://localhost:11434)",
    )
    parser.add_argument(
        "--checkpoint-interval",
        type=int,
        default=50,
        help="Flush assertions to disk every N papers (default: 50)",
    )
    parser.add_argument(
        "--clear-assertions",
        action="store_true",
        help="Delete existing nanopublications and start fresh",
    )
    parser.add_argument(
        "--max-papers",
        type=int,
        default=None,
        help="Max papers to process via LLM (default: no limit)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=None,
        help="Path to YAML config file (overrides checkpoint settings)",
    )
    return parser.parse_args()


def _run_llm_extraction(papers, args, nanopub_path, logger):
    """Run LLM-based assertion extraction (requires Ollama)."""
    llm_config = LLMConfig(
        base_url=args.llm_url,
        model=args.llm_model,
        nanopub_path=str(nanopub_path),
        checkpoint_interval=args.checkpoint_interval,
        max_papers=args.max_papers,
    )
    logger.info(
        "Extracting assertions via LLM (model=%s, checkpoint_interval=%d)...",
        llm_config.model, llm_config.checkpoint_interval,
    )
    logger.info("Nanopub output file: %s", nanopub_path)
    return extract_assertions(papers, llm_config=llm_config)

def main() -> None:
    """Build knowledge graph and score hypotheses."""
    args = parse_args()

    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    logger = logging.getLogger("build_knowledge_graph")

    # Override from config file if provided (or auto-discover)
    config_path = Path(args.config) if args.config else ROOT / "manuscript" / "config.yaml"
    if config_path.exists():
        cfg = _load_kg_config(config_path)
        if not args.config:
            logger.info("Auto-loaded config: %s", config_path)
        if cfg.get("checkpoint_interval") is not None:
            args.checkpoint_interval = cfg["checkpoint_interval"]
            logger.info("Config override: checkpoint_interval = %d", args.checkpoint_interval)
        if cfg.get("clear_assertions") is not None:
            args.clear_assertions = cfg["clear_assertions"]
            logger.info("Config override: clear_assertions = %s", args.clear_assertions)
        if cfg.get("max_papers") is not None and args.max_papers is None:
            args.max_papers = cfg["max_papers"]
            logger.info("Config override: max_papers = %d", args.max_papers)

    # Configure hypotheses from config (or use defaults)
    configure_hypotheses(config_path if config_path.exists() else None)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    # Load corpus
    corpus_path = Path(args.corpus)
    logger.info("Loading corpus from: %s", corpus_path)
    corpus = Corpus.load(corpus_path)
    
    # Filter out anomalous early dates (pre-1960)
    papers = [p for p in corpus.papers if p.year is None or p.year >= 1960]
    logger.info("Loaded %d papers (filtered >= 1960)", len(papers))

    # Single nanopub path — the sole persistence artifact
    nanopub_path = data_dir / "nanopublications.jsonl"

    # Clean up legacy checkpoint file if present
    legacy_checkpoint = output_dir / "llm_checkpoint.jsonl"
    if legacy_checkpoint.exists():
        logger.info(
            "Removing legacy checkpoint file (superseded by nanopublications.jsonl): %s",
            legacy_checkpoint,
        )
        legacy_checkpoint.unlink()

    # Clear assertions if requested (explicit fresh start)
    if args.clear_assertions:
        if nanopub_path.exists():
            nanopub_path.unlink()
            logger.info("Cleared: %s", nanopub_path)

    # --- LLM extraction (incremental by default) ---
    # If nanopublications already exist and we're not clearing, skip LLM extraction
    # and reuse existing assertions for scoring. This avoids requiring network/Ollama.
    if nanopub_path.exists() and not args.clear_assertions:
        all_nanopubs = deserialize_nanopubs(nanopub_path)
        if all_nanopubs:
            logger.info(
                "Nanopublications already exist (%d nanopubs from %d papers) — "
                "skipping LLM extraction. Use --clear-assertions to force re-extraction.",
                len(all_nanopubs),
                len(get_processed_paper_ids(all_nanopubs)),
            )
            assertions = [np.assertion for np in all_nanopubs]
            logger.info("Loaded %d assertions from existing nanopublications", len(assertions))
        else:
            # File exists but empty — fall through to LLM extraction
            all_nanopubs = []
            assertions = _run_llm_extraction(papers, args, nanopub_path, logger)
    else:
        assertions = _run_llm_extraction(papers, args, nanopub_path, logger)
        # Load the final nanopubs from disk (authoritative merged set)
        if nanopub_path.exists():
            all_nanopubs = deserialize_nanopubs(nanopub_path)
        else:
            all_nanopubs = []

    logger.info("Total assertions available: %d", len(assertions))

    # Log nanopub statistics
    if all_nanopubs:
        logger.info(
            "Nanopublications on disk: %d (from %d unique papers) → %s",
            len(all_nanopubs),
            len(get_processed_paper_ids(all_nanopubs)),
            nanopub_path,
        )

    print(str(nanopub_path))

    # Export RDF/TriG per https://nanopub.net/ (Assertion, Provenance, Publication Info)
    if all_nanopubs:
        trig_path = nanopub_path.with_suffix(".trig")
        serialize_nanopubs_to_trig(all_nanopubs, trig_path)
        print(str(trig_path))

    # Score all hypotheses
    logger.info("--- Hypothesis Scoring ---")
    scores = score_all_hypotheses(assertions)
    for hyp_id, score in scores.items():
        direction = "supports" if score > 0 else "contradicts" if score < 0 else "neutral"
        logger.info("  %s: %+.3f (%s)", hyp_id, score, direction)

    scores_path = data_dir / "hypothesis_scores.json"
    with open(scores_path, "w", encoding="utf-8") as f:
        json.dump(scores, f, indent=2)
    print(str(scores_path))

    # Temporal trends
    logger.info("--- Temporal Trends ---")
    yearly_scores = {}
    for hyp_id in HYPOTHESIS_CATEGORIES:
        trend = temporal_trend(assertions, hyp_id, papers)
        if trend:
            yearly_scores[hyp_id] = {str(k): v for k, v in trend.items()}

    trends_path = data_dir / "hypothesis_trends.json"
    with open(trends_path, "w", encoding="utf-8") as f:
        json.dump(yearly_scores, f, indent=2)
    print(str(trends_path))

    # Assertion summary for visualization
    logger.info("--- Assertion Summary ---")
    type_counts: dict[str, int] = {}
    per_hypothesis: dict[str, dict[str, int]] = {}
    for a in assertions:
        type_counts[a.assertion_type] = type_counts.get(a.assertion_type, 0) + 1
        if a.hypothesis_id not in per_hypothesis:
            per_hypothesis[a.hypothesis_id] = {}
        per_hypothesis[a.hypothesis_id][a.assertion_type] = (
            per_hypothesis[a.hypothesis_id].get(a.assertion_type, 0) + 1
        )

    assertion_summary = {
        "total_assertions": len(assertions),
        "type_counts": type_counts,
        "per_hypothesis": per_hypothesis,
    }
    summary_path = data_dir / "assertion_summary.json"
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(assertion_summary, f, indent=2)
    logger.info("Assertion summary: %s", assertion_summary["type_counts"])
    print(str(summary_path))

    # Summary
    logger.info("--- Knowledge Graph Summary ---")
    logger.info("Papers: %d", len(papers))
    logger.info(
        "Assertions: %d (from %d unique papers)",
        len(assertions),
        len(get_processed_paper_ids(all_nanopubs)) if all_nanopubs else 0,
    )
    logger.info("Hypotheses scored: %d", len(scores))
    logger.info("Output directory: %s", output_dir)


if __name__ == "__main__":
    main()
