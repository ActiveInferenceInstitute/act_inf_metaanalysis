"""Data models for literature corpus.

Provides Paper, Author, and Citation dataclasses used throughout
the Active Inference meta-analysis pipeline for representing
bibliographic records, authorship, and citation relationships.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from datetime import date
from typing import Optional


@dataclass
class Author:
    """Represents a paper author.

    Attributes:
        name: Full name (e.g., "Karl Friston")
        affiliation: Institution name, if known
        orcid: ORCID identifier, if known
    """

    name: str
    affiliation: Optional[str] = None
    orcid: Optional[str] = None


@dataclass
class Citation:
    """A directional citation link between two papers.

    Attributes:
        source_id: Canonical ID of the citing paper
        target_id: Canonical ID of the cited paper
        context: Optional citation context text
    """

    source_id: str
    target_id: str
    context: Optional[str] = None


@dataclass
class Paper:
    """Represents a single research paper.

    The canonical_id property returns the best available identifier
    with priority: doi > arxiv_id > s2_id > openalex_id > title hash.

    Attributes:
        title: Paper title
        abstract: Paper abstract text
        authors: List of Author objects
        year: Publication year
        doi: Digital Object Identifier
        arxiv_id: arXiv identifier (e.g., "2301.12345")
        s2_id: Semantic Scholar paper ID
        openalex_id: OpenAlex work ID
        venue: Publication venue/journal
        citation_count: Number of citations
        references: List of canonical IDs this paper cites
        publication_date: Full publication date if available
        pdf_url: Direct URL to a PDF of the full text, if available
        is_open_access: Whether the paper is open access
        full_text_source: Provenance of the full text (e.g., "arxiv",
            "publisher", "repository")
    """

    title: str
    abstract: str = ""
    authors: list[Author] = field(default_factory=list)
    year: Optional[int] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    s2_id: Optional[str] = None
    openalex_id: Optional[str] = None
    venue: Optional[str] = None
    citation_count: int = 0
    references: list[str] = field(default_factory=list)
    publication_date: Optional[date] = None
    pdf_url: Optional[str] = None
    is_open_access: Optional[bool] = None
    full_text_source: Optional[str] = None

    @property
    def canonical_id(self) -> str:
        """Return best available identifier with priority: doi > arxiv_id > s2_id > openalex_id > title hash."""
        if self.doi:
            return f"doi:{self.doi}"
        if self.arxiv_id:
            return f"arxiv:{self.arxiv_id}"
        if self.s2_id:
            return f"s2:{self.s2_id}"
        if self.openalex_id:
            return f"openalex:{self.openalex_id}"
        # Deterministic title fallback: builtin hash() is process-randomized
        # (PYTHONHASHSEED) and can be negative, so it must not be used for a
        # stable cross-run identity. Truncated sha256 matches src/literature/AGENTS.md.
        title_key = self.title.lower().strip()
        digest = hashlib.sha256(title_key.encode("utf-8")).hexdigest()[:16]
        return f"title:{digest}"

    @property
    def metadata_completeness(self) -> int:
        """Count of non-None metadata fields for merge priority.

        Returns:
            Number of populated optional fields.
        """
        count = 0
        if self.abstract:
            count += 1
        if self.authors:
            count += 1
        if self.year is not None:
            count += 1
        if self.doi:
            count += 1
        if self.arxiv_id:
            count += 1
        if self.s2_id:
            count += 1
        if self.openalex_id:
            count += 1
        if self.venue:
            count += 1
        if self.citation_count > 0:
            count += 1
        if self.references:
            count += 1
        if self.publication_date:
            count += 1
        if self.pdf_url:
            count += 1
        if self.is_open_access is not None:
            count += 1
        return count

    def to_dict(self) -> dict:
        """Serialize paper to dictionary for JSONL storage.

        Returns:
            Dictionary representation suitable for JSON serialization.
        """
        return {
            "title": self.title,
            "abstract": self.abstract,
            "authors": [
                {"name": a.name, "affiliation": a.affiliation, "orcid": a.orcid}
                for a in self.authors
            ],
            "year": self.year,
            "doi": self.doi,
            "arxiv_id": self.arxiv_id,
            "s2_id": self.s2_id,
            "openalex_id": self.openalex_id,
            "venue": self.venue,
            "citation_count": self.citation_count,
            "references": self.references,
            "publication_date": self.publication_date.isoformat()
            if self.publication_date
            else None,
            "pdf_url": self.pdf_url,
            "is_open_access": self.is_open_access,
            "full_text_source": self.full_text_source,
        }

    @classmethod
    def from_dict(cls, data: dict) -> Paper:
        """Deserialize paper from dictionary.

        Args:
            data: Dictionary with paper fields.

        Returns:
            Paper instance reconstructed from the dictionary.
        """
        authors = [Author(**a) for a in data.get("authors", [])]
        pub_date = None
        if data.get("publication_date"):
            pub_date = date.fromisoformat(data["publication_date"])
        return cls(
            title=data["title"],
            abstract=data.get("abstract", ""),
            authors=authors,
            year=data.get("year"),
            doi=data.get("doi"),
            arxiv_id=data.get("arxiv_id"),
            s2_id=data.get("s2_id"),
            openalex_id=data.get("openalex_id"),
            venue=data.get("venue"),
            citation_count=data.get("citation_count", 0),
            references=data.get("references", []),
            publication_date=pub_date,
            pdf_url=data.get("pdf_url"),
            is_open_access=data.get("is_open_access"),
            full_text_source=data.get("full_text_source"),
        )
