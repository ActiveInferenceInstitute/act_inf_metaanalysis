"""Nanopublication dataclasses for Active Inference assertions.

Provides Assertion and Nanopublication dataclasses along with factory,
serialization, and deserialization helpers. Nanopublications package a
single assertion together with provenance metadata following the
nanopublication standard (https://nanopub.net/): a small knowledge graph
with (1) Assertion, (2) Provenance, and (3) Publication Info.

- JSON Lines (one JSON object per line) is used for efficient streaming
  and append-friendly storage in the pipeline.
- RDF/TriG export produces standards-compliant nanopublications suitable
  for the nanopublication network and FAIR dissemination.
"""

from __future__ import annotations

import hashlib
import json
import logging
import re
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from rdflib import Dataset

logger = logging.getLogger(__name__)

# RDF namespaces for nanopublication standard (https://nanopub.net/)
NP_NS = "http://www.nanopub.org/nschema#"
PROV_NS = "http://www.w3.org/ns/prov#"
DC_NS = "http://purl.org/dc/terms/"
XSD_NS = "http://www.w3.org/2001/XMLSchema#"
AIF_NS = "http://activeinference.institute/ontology/"
AIF_NANOPUB_BASE = "http://activeinference.institute/nanopub/"
DEFAULT_LICENSE = "https://creativecommons.org/publicdomain/zero/1.0/"


@dataclass
class Assertion:
    """A claim extracted from a paper about an Active Inference concept.

    Three separable layers:
    - **Source claim** (``source_claim_text``, ``evidence_quote``): what the paper states.
    - **Evidence supply** (``evidence_status``, ``evidence_type``): whether evidence is supplied.
    - **Hypothesis triage** (``assertion_type``): pipeline stance toward a hypothesis.

    Attributes:
        assertion_id: Unique identifier for this assertion.
        paper_id: Canonical ID of the source paper.
        claim: LLM reasoning / audit text (justification for the triage).
        assertion_type: Triage direction: ``supports``, ``contradicts``, ``neutral``.
        hypothesis_id: Which hypothesis this relates to.
        confidence: Confidence level in the range ``[0.0, 1.0]``.
        citation_count: Citations of the source paper (used for scoring weight).
        source_claim_text: Explicit claim attributed to the source paper.
        evidence_quote: Verbatim excerpt from abstract supporting the claim.
        evidence_status: ``explicit_claim``, ``mentions``, or ``no_evidence``.
        evidence_type: ``theoretical``, ``empirical``, or ``none``.
    """

    assertion_id: str
    paper_id: str
    claim: str
    assertion_type: str  # hypothesis triage: supports/contradicts/neutral
    hypothesis_id: str
    confidence: float = 1.0
    citation_count: int = 0
    source_claim_text: str = ""
    evidence_quote: str = ""
    evidence_status: str = "mentions"
    evidence_type: str = "none"


@dataclass
class Nanopublication:
    """A nanopublication packaging an assertion with provenance.

    Attributes:
        nanopub_id: Unique identifier for this nanopublication.
        assertion: The core assertion being published.
        attribution: Attribution string (pipeline version + prompt version).
        created_date: ISO-format timestamp of creation.
        provenance: Structured extraction lineage metadata.
    """

    nanopub_id: str
    assertion: Assertion
    attribution: str = ""
    created_date: str = ""
    provenance: dict[str, str] | None = None


def create_nanopub(
    assertion: Assertion,
    attribution: str = "",
    provenance: dict[str, str] | None = None,
    created_date: str | None = None,
    nanopub_id: str | None = None,
) -> Nanopublication:
    """Create a new nanopublication wrapping the given assertion.

    The ``nanopub_id`` is derived deterministically from the assertion identity
    ``(paper_id, hypothesis_id, assertion_type)`` — the same key used by
    :func:`merge_nanopubs` — so a full re-extraction of identical evidence
    produces stable nanopub URIs (reproducible RDF/JSONL), and mixed-direction
    assessments for one paper+hypothesis get distinct, non-colliding IDs.

    Args:
        assertion: The assertion to wrap.
        attribution: Optional attribution string (e.g. author or pipeline name).
        provenance: Structured extraction lineage metadata.
        created_date: Optional ISO-8601 creation timestamp; defaults to `now`
            (a real run time, so provenance remains honest — reproducibility
            is anchored by the nanopub id, not by backdating timestamps).
        nanopub_id: Optional explicit id; defaults to a deterministic digest.

    Returns:
        A fully populated Nanopublication instance.
    """
    if nanopub_id is None:
        key = (
            f"{assertion.paper_id}|{assertion.hypothesis_id}|"
            f"{assertion.assertion_type}"
        )
        digest = hashlib.sha256(key.encode("utf-8")).hexdigest()[:24]
        nanopub_id = f"nanopub:{digest}"
    if created_date is None:
        created_date = datetime.now(timezone.utc).isoformat()
    return Nanopublication(
        nanopub_id=nanopub_id,
        assertion=assertion,
        attribution=attribution,
        created_date=created_date,
        provenance=provenance,
    )


def nanopub_to_dict(nanopub: Nanopublication) -> dict:
    """Serialize a Nanopublication to a plain dictionary.

    Args:
        nanopub: The nanopublication to serialize.

    Returns:
        Dictionary suitable for JSON serialization.
    """
    payload = {
        "nanopub_id": nanopub.nanopub_id,
        "assertion": {
            "assertion_id": nanopub.assertion.assertion_id,
            "paper_id": nanopub.assertion.paper_id,
            "claim": nanopub.assertion.claim,
            "assertion_type": nanopub.assertion.assertion_type,
            "hypothesis_id": nanopub.assertion.hypothesis_id,
            "confidence": nanopub.assertion.confidence,
            "citation_count": nanopub.assertion.citation_count,
            "source_claim_text": nanopub.assertion.source_claim_text,
            "evidence_quote": nanopub.assertion.evidence_quote,
            "evidence_status": nanopub.assertion.evidence_status,
            "evidence_type": nanopub.assertion.evidence_type,
        },
        "attribution": nanopub.attribution,
        "created_date": nanopub.created_date,
    }
    if nanopub.provenance:
        payload["provenance"] = nanopub.provenance
    return payload


def nanopub_from_dict(data: dict) -> Nanopublication:
    """Deserialize a Nanopublication from a plain dictionary.

    Args:
        data: Dictionary previously produced by ``nanopub_to_dict``.

    Returns:
        Reconstructed Nanopublication instance.
    """
    a = data["assertion"]
    assertion = Assertion(
        assertion_id=a["assertion_id"],
        paper_id=a["paper_id"],
        claim=a["claim"],
        assertion_type=a["assertion_type"],
        hypothesis_id=a["hypothesis_id"],
        confidence=a.get("confidence", 1.0),
        citation_count=a.get("citation_count", 0),
        source_claim_text=a.get("source_claim_text", ""),
        evidence_quote=a.get("evidence_quote", ""),
        evidence_status=a.get("evidence_status", "mentions"),
        evidence_type=a.get("evidence_type", "none"),
    )
    return Nanopublication(
        nanopub_id=data["nanopub_id"],
        assertion=assertion,
        attribution=data.get("attribution", ""),
        created_date=data.get("created_date", ""),
        provenance=data.get("provenance"),
    )


def serialize_nanopubs(nanopubs: list[Nanopublication], path: Path) -> None:
    """Write nanopublications to a JSON Lines file.

    Each line contains one JSON object representing a single nanopublication.

    Args:
        nanopubs: List of nanopublications to serialize.
        path: Destination file path (will be overwritten if it exists).
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        for np_obj in nanopubs:
            line = json.dumps(nanopub_to_dict(np_obj), ensure_ascii=False)
            fh.write(line + "\n")


def deserialize_nanopubs(path: Path) -> list[Nanopublication]:
    """Read nanopublications from a JSON Lines file.

    Args:
        path: Source file path containing one JSON object per line.

    Returns:
        List of deserialized Nanopublication instances.
    """
    nanopubs: list[Nanopublication] = []
    with open(path, "r", encoding="utf-8") as fh:
        for lineno, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                data = json.loads(line)
                nanopubs.append(nanopub_from_dict(data))
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                # Fail with a precise, line-numbered message so a single corrupt
                # record is trivially located and repaired (MED-13).
                raise ValueError(
                    f"Malformed nanopublication record at {path}:{lineno}: {exc}"
                ) from exc
    return nanopubs


def merge_nanopubs(
    existing: list[Nanopublication],
    new: list[Nanopublication],
) -> list[Nanopublication]:
    """Merge two lists of nanopublications, deduplicating by assertion key.

    The composite key ``(paper_id, hypothesis_id, assertion_type)`` uniquely
    identifies an assertion direction; a single paper can legitimately carry
    both a ``supports`` and a ``contradicts`` assessment for the same
    hypothesis (mixed evidence), and collapsing them would silently drop one
    direction and bias the citation-weighted score. When an exact duplicate
    (same paper, hypothesis, and direction) exists, the *new* entry wins so
    that re-runs with improved models can overwrite stale results.

    Args:
        existing: Previously saved nanopublications.
        new: Freshly extracted nanopublications to merge in.

    Returns:
        Merged list with duplicates removed.
    """
    seen: dict[tuple[str, str, str], Nanopublication] = {}
    for np_obj in existing:
        key = (
            np_obj.assertion.paper_id,
            np_obj.assertion.hypothesis_id,
            np_obj.assertion.assertion_type,
        )
        seen[key] = np_obj
    for np_obj in new:
        key = (
            np_obj.assertion.paper_id,
            np_obj.assertion.hypothesis_id,
            np_obj.assertion.assertion_type,
        )
        seen[key] = np_obj  # new wins per direction
    return list(seen.values())


def get_processed_paper_ids(nanopubs: list[Nanopublication]) -> set[str]:
    """Extract the set of unique paper IDs from nanopublications.

    Useful for determining which papers have already been processed
    so that incremental runs can skip them.

    Args:
        nanopubs: List of nanopublications to inspect.

    Returns:
        Set of canonical paper IDs.
    """
    return {np_obj.assertion.paper_id for np_obj in nanopubs}


def append_nanopubs(
    new_nanopubs: list[Nanopublication],
    path: Path,
) -> list[Nanopublication]:
    """Atomically append nanopublications to an existing JSONL file.

    Reads the existing file (if present), merges with the new entries
    (deduplicating by ``(paper_id, hypothesis_id)`` — new wins), and
    writes the result atomically via a temporary file + rename.

    This is the **single source of truth** for incremental persistence:
    every checkpoint flush writes directly to the nanopublications file
    so that interrupts never lose already-checkpointed work.

    Args:
        new_nanopubs: Freshly extracted nanopublications to persist.
        path: Destination JSONL file (created if absent).

    Returns:
        The merged list of all nanopublications now on disk.
    """
    path.parent.mkdir(parents=True, exist_ok=True)
    existing = deserialize_nanopubs(path) if path.exists() else []
    merged = merge_nanopubs(existing, new_nanopubs)
    # Atomic write: temp file → rename
    tmp = path.with_suffix(".jsonl.tmp")
    serialize_nanopubs(merged, tmp)
    tmp.rename(path)
    logger.info(
        "📄 Wrote %d nanopubs → %s",
        len(merged), path,
    )
    return merged


def _nanopub_resource_uri(nanopub_id: str, base_uri: str = AIF_NANOPUB_BASE) -> str:
    """Turn nanopub_id (e.g. nanopub:abc123) into a full resource URI."""
    local = nanopub_id.replace("nanopub:", "").strip()
    if not local:
        local = uuid.uuid4().hex[:12]
    return base_uri.rstrip("/") + "/" + local


def _safe_uri_fragment(s: str) -> str:
    """Replace characters that are unsafe in URI fragments."""
    return re.sub(r"[^A-Za-z0-9_.-]", "_", s)


def nanopub_to_rdf(
    nanopub: Nanopublication,
    base_uri: str = AIF_NANOPUB_BASE,
) -> "Dataset":
    """Serialize a single nanopublication to RDF (TriG) per https://nanopub.net/.

    Produces a nanopublication with four named graphs:
    - **Head**: the nanopub resource with np:hasAssertion, np:hasProvenance,
      np:hasPublicationInfo linking to the three graphs below.
    - **Assertion**: the main content (paper → assertion → hypothesis; claim;
      confidence; citation count).
    - **Provenance**: how the assertion was generated (agent, time, method).
    - **Publication info**: creator, created date, license.

    Args:
        nanopub: The nanopublication to serialize.
        base_uri: Base URI for nanopub resources (default Active Inference).

    Returns:
        An rdflib Dataset containing the four named graphs for this nanopub.
    """
    from rdflib import Dataset, Literal, Namespace, URIRef
    from rdflib.namespace import RDF

    np_ns = Namespace(NP_NS)
    prov_ns = Namespace(PROV_NS)
    dc_ns = Namespace(DC_NS)
    aif_ns = Namespace(AIF_NS)
    xsd_ns = Namespace(XSD_NS)
    np_nanopub_class = URIRef(NP_NS + "Nanopublication")

    ds: Dataset = Dataset()
    np_uri = _nanopub_resource_uri(nanopub.nanopub_id, base_uri)
    head_uri = URIRef(np_uri + "#head")
    assertion_graph_uri = URIRef(np_uri + "#assertion")
    provenance_graph_uri = URIRef(np_uri + "#provenance")
    pubinfo_graph_uri = URIRef(np_uri + "#pubinfo")

    np_res = URIRef(np_uri)
    a = nanopub.assertion
    paper_uri = URIRef(aif_ns["paper/" + _safe_uri_fragment(a.paper_id)])
    assertion_uri = URIRef(aif_ns["assertion/" + _safe_uri_fragment(a.assertion_id)])
    hypothesis_uri = URIRef(aif_ns["hypothesis/" + a.hypothesis_id.lower()])

    # Head graph: this nanopublication links to the three components (nanopub.net)
    head_g = ds.graph(head_uri)
    head_g.add((np_res, np_ns.hasAssertion, assertion_graph_uri))
    head_g.add((np_res, np_ns.hasProvenance, provenance_graph_uri))
    head_g.add((np_res, np_ns.hasPublicationInfo, pubinfo_graph_uri))
    head_g.add((np_res, RDF.type, np_nanopub_class))

    # Assertion graph: main content (atomic unit of information)
    assn_g = ds.graph(assertion_graph_uri)
    assn_g.add((paper_uri, aif_ns["asserts"], assertion_uri))
    if a.assertion_type == "supports":
        assn_g.add((assertion_uri, aif_ns["supports"], hypothesis_uri))
    elif a.assertion_type == "contradicts":
        assn_g.add((assertion_uri, aif_ns["contradicts"], hypothesis_uri))
    else:
        assn_g.add((assertion_uri, aif_ns["neutral"], hypothesis_uri))
    assn_g.add((assertion_uri, aif_ns["claim"], Literal(a.claim, datatype=xsd_ns.string)))
    if a.source_claim_text:
        assn_g.add(
            (assertion_uri, aif_ns["sourceClaim"], Literal(a.source_claim_text, datatype=xsd_ns.string))
        )
    if a.evidence_quote:
        assn_g.add(
            (assertion_uri, aif_ns["evidenceQuote"], Literal(a.evidence_quote, datatype=xsd_ns.string))
        )
    assn_g.add(
        (assertion_uri, aif_ns["evidenceStatus"], Literal(a.evidence_status, datatype=xsd_ns.string))
    )
    assn_g.add(
        (assertion_uri, aif_ns["evidenceType"], Literal(a.evidence_type, datatype=xsd_ns.string))
    )
    assn_g.add((assertion_uri, aif_ns["confidence"], Literal(a.confidence, datatype=xsd_ns.double)))
    assn_g.add((assertion_uri, aif_ns["citationCount"], Literal(a.citation_count, datatype=xsd_ns.integer)))

    # Provenance graph: how the assertion came to be
    prov_g = ds.graph(provenance_graph_uri)
    prov_g.add((assertion_uri, prov_ns.wasGeneratedBy, np_res))
    if nanopub.created_date:
        prov_g.add((assertion_uri, prov_ns.generatedAtTime, Literal(nanopub.created_date, datatype=xsd_ns.dateTime)))
    if nanopub.attribution:
        prov_g.add((assertion_uri, prov_ns.wasAttributedTo, Literal(nanopub.attribution, datatype=xsd_ns.string)))
    prov_g.add((assertion_uri, prov_ns.hadPrimarySource, paper_uri))
    if nanopub.provenance:
        for key, value in nanopub.provenance.items():
            if value:
                prov_g.add(
                    (
                        assertion_uri,
                        aif_ns[f"prov_{key}"],
                        Literal(str(value), datatype=xsd_ns.string),
                    )
                )

    # Publication info graph: metadata about the nanopublication
    pub_g = ds.graph(pubinfo_graph_uri)
    pub_g.add((np_res, dc_ns.created, Literal(nanopub.created_date or "", datatype=xsd_ns.dateTime)))
    if nanopub.attribution:
        pub_g.add((np_res, dc_ns.creator, Literal(nanopub.attribution, datatype=xsd_ns.string)))
    pub_g.add((np_res, dc_ns.license, URIRef(DEFAULT_LICENSE)))

    return ds


def serialize_nanopubs_to_trig(
    nanopubs: list[Nanopublication],
    path: Path,
    base_uri: str = AIF_NANOPUB_BASE,
) -> None:
    """Write nanopublications to a TriG file in RDF format per https://nanopub.net/.

    Each nanopublication is represented as four named graphs (head, assertion,
    provenance, publication info). The resulting file can be published to the
    nanopublication network and is suitable for FAIR dissemination.

    Args:
        nanopubs: List of nanopublications to serialize.
        path: Destination .trig file path (will be overwritten if exists).
        base_uri: Base URI for nanopub resources.
    """
    from rdflib import Dataset

    path.parent.mkdir(parents=True, exist_ok=True)
    combined: Dataset = Dataset()
    for np_obj in nanopubs:
        ds = nanopub_to_rdf(np_obj, base_uri)
        for g in ds.graphs():
            for t in g:
                combined.get_context(g.identifier).add(t)
    combined.serialize(destination=str(path), format="trig", encoding="utf-8")
    logger.info("📄 Wrote %d nanopublication(s) in RDF/TriG → %s", len(nanopubs), path)
