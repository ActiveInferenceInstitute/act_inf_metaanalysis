"""Pure validation helpers for the dated tooling-source survey."""

from __future__ import annotations

from collections import Counter
from typing import Any

TOOLING_VERIFICATION_SCHEMA_VERSION = "1.0"

# These are source pointers, not claims that every project has a maintained
# repository.  The network probe records that distinction explicitly.
TOOLING_SOURCES: dict[str, dict[str, str]] = {
    "pymdp": {"url": "https://api.github.com/repos/infer-actively/pymdp", "kind": "github"},
    "spm": {"url": "https://www.fil.ion.ucl.ac.uk/spm/software/spm12/", "kind": "official_site"},
    "rxinfer": {"url": "https://api.github.com/repos/ReactiveBayes/RxInfer.jl", "kind": "github"},
    "activeinference_jl": {"url": "https://api.github.com/repos/ilabcode/ActiveInference.jl", "kind": "github"},
    "cpp_aif": {"url": "https://api.github.com/repos/fgregoretti/Cpp-AIF", "kind": "github"},
    "feps": {"url": "https://arxiv.org/abs/2411.14991", "kind": "preprint"},
    "deep_active_inference_mc": {"url": "https://api.github.com/repos/zfountas/deep-active-inference-mc", "kind": "github"},
    "deep_active_inference": {"url": "https://api.github.com/repos/BerenMillidge/DeepActiveInference", "kind": "github"},
    "btai_3mf": {"url": "https://api.github.com/repos/ChampiB/BTAI_3MF", "kind": "github"},
    "deep_btai_3mf": {"url": "https://api.github.com/repos/ChampiB/BTAI_3MF", "kind": "github"},
    "axiom": {"url": "https://arxiv.org/abs/2505.24784", "kind": "preprint"},
    "active_inference_voostrum": {"url": "https://arxiv.org/abs/2406.07726", "kind": "preprint"},
    "predictive_coding_backprop": {"url": "https://api.github.com/repos/BerenMillidge/PredictiveCodingBackprop", "kind": "github"},
    "ants": {"url": "https://api.github.com/repos/conorheins/collective_motion_actinf", "kind": "github"},
    "action_oriented": {"url": "https://api.github.com/repos/alec-tschantz/action-oriented", "kind": "github"},
    "bayesian_mechanics_sdes": {"url": "https://api.github.com/repos/conorheins/bayesian-mechanics-sdes", "kind": "github"},
    "adaptive_aif_agents_fl": {"url": "https://api.github.com/repos/adanilenka/adaptive_aif_agents_for_fl", "kind": "github"},
    "rl_inference": {"url": "https://arxiv.org/abs/2002.12636", "kind": "preprint"},
    "robust_fe_minimization": {"url": "https://arxiv.org/abs/2503.13223", "kind": "preprint"},
}


def build_tooling_verification_report(
    registry: dict[str, Any],
    observations: list[dict[str, Any]],
    *,
    checked_at: str,
) -> dict[str, Any]:
    """Combine registry rows with dated source observations.

    A row is ``verified`` only when the source is reachable, the source is
    repository-backed, a license is explicitly reported, and the repository
    is not archived.  Paper-only or incomplete rows remain ``flagged`` so the
    publication table cannot silently overstate software availability.
    """
    entries = registry.get("retained_tools", [])
    registry_ids = [str(entry.get("id", "")) for entry in entries]
    by_id = {str(item.get("id", "")): item for item in observations}
    results: list[dict[str, Any]] = []
    for entry in entries:
        tool_id = str(entry.get("id", ""))
        observation = by_id.get(tool_id, {})
        status = str(observation.get("status", "missing"))
        if status not in {"verified", "flagged"}:
            status = "flagged"
        results.append({
            "id": tool_id,
            "display_name": entry.get("display_name", tool_id),
            "evidence": entry.get("evidence"),
            "evidence_type": entry.get("evidence_type"),
            **observation,
            "status": status,
        })
    missing_ids = sorted(set(registry_ids) - set(by_id))
    unknown_ids = sorted(set(by_id) - set(registry_ids))
    counts = Counter(item["status"] for item in results)
    errors = []
    if missing_ids:
        errors.append(f"missing observations for: {', '.join(missing_ids)}")
    if unknown_ids:
        errors.append(f"observations for unknown tools: {', '.join(unknown_ids)}")
    warnings = [
        f"{item['id']}: {', '.join(item.get('flags', []))}"
        for item in results
        if item["status"] == "flagged"
    ]
    return {
        "schema_version": TOOLING_VERIFICATION_SCHEMA_VERSION,
        "checked_at": checked_at,
        "status": "pass" if not errors and not warnings else "fail",
        "errors": errors,
        "warnings": warnings,
        "registry_count": len(entries),
        "verified_count": counts.get("verified", 0),
        "flagged_count": counts.get("flagged", 0),
        "results": results,
    }


__all__ = [
    "TOOLING_SOURCES",
    "TOOLING_VERIFICATION_SCHEMA_VERSION",
    "build_tooling_verification_report",
]
