"""Prompt templates for LLM hypothesis assessment."""

from __future__ import annotations

import knowledge_graph.hypothesis as _hypothesis_module
from knowledge_graph.provenance import PROMPT_VERSION
from literature.models import Paper

_SYSTEM_PROMPT = """\
You are a scientific literature analyst specialising in Active Inference \
and the Free Energy Principle. You will receive a paper's title and \
abstract, together with a list of research hypotheses.

For each hypothesis, return THREE separable layers:
1. **source_claim_text** — what the paper explicitly states (one sentence).
2. **evidence supply** — ``evidence_status`` (explicit_claim | mentions | no_evidence) \
and ``evidence_type`` (theoretical | empirical | none).
3. **hypothesis triage** — ``direction`` (supports | contradicts | neutral | irrelevant) \
reflecting whether the paper's claim bears on the hypothesis.

Return ONLY a JSON array (no markdown fences, no commentary). Each \
element must include:

  "hypothesis_id", "direction", "confidence", "reasoning",
  "source_claim_text", "evidence_quote", "evidence_status", "evidence_type"
"""


def build_prompt(paper: Paper, hypotheses: list[dict[str, str]]) -> str:
    """Build the user-turn prompt for a single paper."""
    hyp_block = "\n".join(
        f"  - {h['id']}: {h['name']} — {h['description']}" for h in hypotheses
    )
    return (
        f"## Paper\n"
        f"**Title:** {paper.title}\n"
        f"**Abstract:** {paper.abstract}\n\n"
        f"## Hypotheses to assess\n{hyp_block}\n\n"
        f"Respond with the JSON array now."
    )


def hypothesis_dicts() -> list[dict[str, str]]:
    """Convert configured hypotheses to prompt dicts."""
    return [
        {"id": h.hypothesis_id, "name": h.name, "description": h.description}
        for h in _hypothesis_module.HYPOTHESES
    ]


def prompt_version() -> str:
    """Return the active prompt schema version."""
    return PROMPT_VERSION
