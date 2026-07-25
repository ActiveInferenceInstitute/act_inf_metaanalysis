"""Knowledge graph construction and hypothesis scoring pipeline."""

from __future__ import annotations

import argparse
import json
import logging
from pathlib import Path

import knowledge_graph.schema as _schema
from config_loader import load_kg_config
from knowledge_graph.extraction import extract_assertions
from knowledge_graph.hypothesis import (
    configure_hypotheses,
    score_all_hypotheses,
    temporal_trend,
    temporal_trend_with_counts,
)
from knowledge_graph.llm_extraction import LLMConfig
from knowledge_graph.nanopublication import (
    deserialize_nanopubs,
    get_processed_paper_ids,
    serialize_nanopubs_to_trig,
)
from knowledge_graph.provenance import write_provenance_summary
from knowledge_graph.sensitivity import write_sensitivity_analysis
from literature.corpus import Corpus


def _run_llm_extraction(papers, args, nanopub_path, kg_cfg, logger):
    llm_config = LLMConfig(
        base_url=args.llm_url,
        model=args.llm_model,
        nanopub_path=str(nanopub_path),
        checkpoint_interval=args.checkpoint_interval,
        max_papers=args.max_papers,
        temperature=kg_cfg.get("llm_temperature") or 0.1,
        max_tokens=kg_cfg.get("llm_max_tokens") or 2048,
        timeout_seconds=kg_cfg.get("llm_timeout") or 120,
        max_retries=kg_cfg.get("llm_max_retries") or 3,
        min_confidence=kg_cfg.get("llm_min_confidence") or 0.0,
        worker_urls=(
            ()
            if getattr(args, "_llm_url_cli", False)
            else tuple(kg_cfg.get("worker_urls") or ())
        ),
    )
    logger.info(
        "Extracting assertions via LLM (model=%s, checkpoint_interval=%d)...",
        llm_config.model,
        llm_config.checkpoint_interval,
    )
    return extract_assertions(
        papers,
        llm_config=llm_config,
        pipeline_version=kg_cfg.get("pipeline_version"),
    )


def run_knowledge_graph_pipeline(args: argparse.Namespace, *, project_root: Path) -> None:
    """Build knowledge graph artifacts and score hypotheses."""
    logger = logging.getLogger("build_knowledge_graph")
    config_path = Path(args.config) if args.config else project_root / "manuscript" / "config.yaml"
    kg_cfg = load_kg_config(config_path) if config_path.exists() else {}

    if config_path.exists() and not args.config:
        logger.info("Auto-loaded config: %s", config_path)
    if kg_cfg.get("checkpoint_interval") is not None:
        args.checkpoint_interval = kg_cfg["checkpoint_interval"]
    # Config may REQUEST a clear, but must never silently override an explicit
    # CLI --clear-assertions. CLI True always wins; config True also enables it.
    args.clear_assertions = bool(args.clear_assertions) or bool(
        kg_cfg.get("clear_assertions", False)
    )
    if kg_cfg.get("max_papers") is not None and args.max_papers is None:
        args.max_papers = kg_cfg["max_papers"]
    if kg_cfg.get("llm_model") and not getattr(args, "_llm_model_cli", False):
        args.llm_model = kg_cfg["llm_model"]
    if kg_cfg.get("llm_url") and not getattr(args, "_llm_url_cli", False):
        args.llm_url = kg_cfg["llm_url"]
    if args.llm_model is None:
        args.llm_model = "gemma3:4b"
    if args.llm_url is None:
        args.llm_url = "http://localhost:11434"

    configure_hypotheses(config_path if config_path.exists() else None)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)

    from config import KG_MIN_YEAR

    corpus = Corpus.load(Path(args.corpus))
    papers = [p for p in corpus.papers if p.year is None or p.year >= KG_MIN_YEAR]
    logger.info("Loaded %d papers (filtered >= %d)", len(papers), KG_MIN_YEAR)

    nanopub_path = data_dir / "nanopublications.jsonl"
    stale_checkpoint = output_dir / "llm_checkpoint.jsonl"
    if stale_checkpoint.exists():
        stale_checkpoint.unlink()

    if args.clear_assertions and nanopub_path.exists():
        nanopub_path.unlink()

    all_nanopubs = deserialize_nanopubs(nanopub_path) if nanopub_path.exists() else []
    processed_ids = get_processed_paper_ids(all_nanopubs) if all_nanopubs else set()
    pending = [
        p for p in papers if p.abstract and p.canonical_id not in processed_ids
    ]

    if all_nanopubs and not pending and not args.clear_assertions:
        assertions = [np_obj.assertion for np_obj in all_nanopubs]
        logger.info("Skipping LLM extraction — corpus already covered.")
    else:
        assertions = _run_llm_extraction(papers, args, nanopub_path, kg_cfg, logger)
        if nanopub_path.exists():
            all_nanopubs = deserialize_nanopubs(nanopub_path)

    coverage_path = data_dir / "extraction_coverage.json"
    if coverage_path.exists():
        with open(coverage_path, encoding="utf-8") as handle:
            coverage = json.load(handle)
        if coverage.get("unprocessed_papers", 0) or coverage.get("failed_papers", 0):
            raise RuntimeError(
                "LLM extraction coverage is incomplete: "
                f"{coverage.get('failed_papers', 0)} failed, "
                f"{coverage.get('unprocessed_papers', 0)} unprocessed"
            )
    elif papers and not (all_nanopubs and not pending and not args.clear_assertions):
        raise RuntimeError("Missing extraction_coverage.json after LLM extraction")
    elif all_nanopubs and not pending and not args.clear_assertions:
        logger.warning("Nanopublication fixture has no extraction coverage report")

    print(str(nanopub_path))
    if all_nanopubs:
        trig_path = nanopub_path.with_suffix(".trig")
        serialize_nanopubs_to_trig(all_nanopubs, trig_path)
        print(str(trig_path))

    scores = score_all_hypotheses(assertions)
    scores_path = data_dir / "hypothesis_scores.json"
    with open(scores_path, "w", encoding="utf-8") as handle:
        json.dump(scores, handle, indent=2)
    print(str(scores_path))

    yearly_scores = {}
    for hyp_id in _schema.HYPOTHESIS_CATEGORIES:
        trend = temporal_trend_with_counts(assertions, hyp_id, papers)
        if trend:
            yearly_scores[hyp_id] = {str(k): v for k, v in trend.items()}

    trends_path = data_dir / "hypothesis_trends.json"
    with open(trends_path, "w", encoding="utf-8") as handle:
        json.dump(yearly_scores, handle, indent=2)
    print(str(trends_path))

    type_counts: dict[str, int] = {}
    per_hypothesis: dict[str, dict[str, int]] = {}
    for assertion in assertions:
        type_counts[assertion.assertion_type] = (
            type_counts.get(assertion.assertion_type, 0) + 1
        )
        bucket = per_hypothesis.setdefault(assertion.hypothesis_id, {})
        bucket[assertion.assertion_type] = bucket.get(assertion.assertion_type, 0) + 1

    summary_path = data_dir / "assertion_summary.json"
    with open(summary_path, "w", encoding="utf-8") as handle:
        json.dump(
            {
                "total_assertions": len(assertions),
                "type_counts": type_counts,
                "per_hypothesis": per_hypothesis,
            },
            handle,
            indent=2,
        )
    print(str(summary_path))

    sensitivity_path = data_dir / "hypothesis_sensitivity.json"
    write_sensitivity_analysis(
        assertions, papers, sensitivity_path,
        config_path if config_path.exists() else None,
    )
    print(str(sensitivity_path))

    provenance_report = output_dir / "reports" / "extraction_provenance_summary.json"
    write_provenance_summary(nanopub_path, provenance_report)
    print(str(provenance_report))
