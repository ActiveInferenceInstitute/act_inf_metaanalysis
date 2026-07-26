"""Semantic Scholar Graph API client.

Provides functions to bulk-search papers, retrieve paper details, and fetch
citation relationships via the Semantic Scholar API. All functions accept an
injectable base_url for testing with pytest-httpserver.

Bulk search uses the API's continuation-token endpoint so a large retrieval is
served by one request whenever possible. Detail and citation calls retain the
full nested field set, while bulk search requests only fields supported by the
bulk endpoint. All requests use bounded Retry-After-aware backoff and
structured rate-limit diagnostics.

API reference: https://api.semanticscholar.org/api-docs/graph
"""

from __future__ import annotations

import logging
import os
import random
import time
from email.utils import parsedate_to_datetime
from typing import Callable, Optional

import requests

from .models import Author, Citation, Paper

logger = logging.getLogger(__name__)

# Default API base URL
S2_API_URL = "https://api.semanticscholar.org/graph/v1"
S2_BULK_SEARCH_PATH = "/paper/search/bulk"
S2_DETAIL_FIELDS = "title,abstract,authors,year,externalIds,citationCount,venue,references,isOpenAccess,openAccessPdf"
S2_BULK_SEARCH_FIELDS = "title,abstract,authors,year,externalIds,citationCount,venue,isOpenAccess,openAccessPdf"
S2_USER_AGENT = "act-inf-metaanalysis/2.0.6 (+https://github.com/ActiveInferenceInstitute/act_inf_metaanalysis)"

# Fields we request from the API
PAPER_FIELDS = S2_DETAIL_FIELDS
CITATION_FIELDS = "title,authors,year,externalIds"

# Retry settings
MAX_RETRIES = 3
RETRY_BASE_SECONDS = 10.0
MAX_BACKOFF_SECONDS = 60.0
TRANSIENT_STATUS_CODES = frozenset({429, 500, 502, 503, 504})

# Bulk-search pagination. The API accepts up to 1,000 rows per request and
# returns a continuation token when more matches remain.
S2_BULK_PAGE_SIZE = 1000


class SemanticScholarRateLimitError(requests.HTTPError):
    """A bounded Semantic Scholar 429 failure with safe diagnostic fields."""

    status_code = 429
    rate_limited = True

    def __init__(
        self,
        *,
        url: str,
        attempts: int,
        api_key_configured: bool,
        retry_after: float | None,
        response_body: str,
    ) -> None:
        self.attempts = attempts
        self.api_key_configured = api_key_configured
        self.retry_after = retry_after
        self.response_body = response_body[:240]
        key_status = "configured" if api_key_configured else "not configured"
        retry_status = (
            f"Retry-After={retry_after:.1f}s"
            if retry_after is not None
            else "Retry-After=absent"
        )
        super().__init__(
            "Semantic Scholar returned HTTP 429 after "
            f"{attempts} attempts ({retry_status}; API key {key_status}; url={url}). "
            "Configure an API key or retry after the service releases the throttle."
        )


def _parse_s2_paper(data: dict) -> Paper:
    """Parse a Semantic Scholar paper JSON object into a Paper.

    Args:
        data: Dictionary from the S2 API representing a paper.

    Returns:
        Paper object populated from the API data.
    """
    # Authors
    authors = []
    for a in data.get("authors", []) or []:
        name = a.get("name") or a.get("authorId", "Unknown")
        authors.append(Author(name=name))

    # External IDs
    ext_ids = data.get("externalIds") or {}
    doi = ext_ids.get("DOI")
    arxiv_id = ext_ids.get("ArXiv")

    # References (list of paper IDs)
    references = []
    for ref in data.get("references", []) or []:
        if isinstance(ref, dict) and ref.get("paperId"):
            references.append(f"s2:{ref['paperId']}")
        elif isinstance(ref, str):
            references.append(f"s2:{ref}")

    # Open access and PDF URL
    is_open_access = data.get("isOpenAccess")
    pdf_url = None
    full_text_source = None
    oa_pdf = data.get("openAccessPdf")
    if isinstance(oa_pdf, dict) and oa_pdf.get("url"):
        pdf_url = oa_pdf["url"]
        full_text_source = "semantic_scholar"

    return Paper(
        title=data.get("title", ""),
        abstract=data.get("abstract") or "",
        authors=authors,
        year=data.get("year"),
        doi=doi,
        arxiv_id=arxiv_id,
        s2_id=data.get("paperId"),
        venue=data.get("venue") or None,
        citation_count=data.get("citationCount") or 0,
        references=references,
        pdf_url=pdf_url,
        is_open_access=is_open_access,
        full_text_source=full_text_source,
    )


def _request_with_retry(
    http: requests.Session,
    url: str,
    params: dict,
    max_retries: int = MAX_RETRIES,
    max_backoff_seconds: float = MAX_BACKOFF_SECONDS,
    api_key: str | None = None,
    delay_override: Optional[Callable[[float], None]] = None,
) -> requests.Response:
    """Make an HTTP GET request with bounded transient-error retries.

    Uses exponential backoff with jitter to avoid thundering herd.

    Args:
        http: requests.Session for the request.
        url: URL to request.
        params: Query parameters.
        max_retries: Maximum number of retry attempts.
        delay_override: Optional sleep function (test injection).

    Returns:
        Successful response object.

    Raises:
        requests.RequestException: If a transport or HTTP error remains after
            the bounded retry budget.
    """
    sleep_fn = delay_override or time.sleep
    headers = {
        "Accept": "application/json",
        "User-Agent": S2_USER_AGENT,
    }
    if api_key:
        # Semantic Scholar documents this exact header spelling for API keys.
        headers["x-api-key"] = api_key
    response: requests.Response | None = None
    last_transport_error: requests.RequestException | None = None
    for attempt in range(max_retries + 1):
        try:
            response = http.get(url, params=params, headers=headers, timeout=30)
            last_transport_error = None
        except (requests.ConnectionError, requests.Timeout) as exc:
            last_transport_error = exc
            if attempt == max_retries:
                raise
            wait = min(
                max_backoff_seconds,
                max(0.0, RETRY_BASE_SECONDS * (2 ** attempt) + random.uniform(0, 1)),
            )
            logger.warning(
                "S2 transport error (%s), retry %d/%d after %.1fs",
                type(exc).__name__, attempt + 1, max_retries, wait,
            )
            sleep_fn(wait)
            continue

        if response.status_code not in TRANSIENT_STATUS_CODES:
            response.raise_for_status()
            return response
        if attempt == max_retries:
            break

        retry_after = _retry_after_seconds(response.headers.get("Retry-After"))
        wait = retry_after if retry_after is not None else (
            RETRY_BASE_SECONDS * (2 ** attempt) + random.uniform(0, 1)
        )
        wait = min(max_backoff_seconds, max(0.0, wait))
        logger.warning(
            "S2 transient HTTP %d, retry %d/%d after %.1fs",
            response.status_code, attempt + 1, max_retries, wait,
        )
        sleep_fn(wait)

    # All retries exhausted
    logger.error(
        "S2 transient retries exhausted after %d retries (status=%s, url=%s, query=%s)",
        max_retries,
        response.status_code if response is not None else "transport",
        url,
        params.get("query", ""),
    )
    if response is not None and response.status_code == 429:
        raise SemanticScholarRateLimitError(
            url=url,
            attempts=max_retries + 1,
            api_key_configured=bool(api_key),
            retry_after=_retry_after_seconds(response.headers.get("Retry-After")),
            response_body=response.text,
        ) from None
    if response is not None:
        response.raise_for_status()
    if last_transport_error is not None:  # pragma: no cover - final transport errors re-raise above
        raise last_transport_error
    raise requests.HTTPError("Semantic Scholar request retries exhausted")  # pragma: no cover


def _retry_after_seconds(value: str | None) -> float | None:
    """Parse numeric or HTTP-date ``Retry-After`` values."""
    if not value:
        return None
    try:
        return max(0.0, float(value))
    except ValueError:
        pass
    try:
        retry_at = parsedate_to_datetime(value)
        if retry_at.tzinfo is None:
            retry_at = retry_at.astimezone()
        return max(0.0, retry_at.timestamp() - time.time())
    except (TypeError, ValueError, OverflowError):
        return None


def search_semantic_scholar(
    query: str,
    max_results: int = 100,
    base_url: str = S2_API_URL,
    session: Optional[requests.Session] = None,
    delay_override: Optional[Callable[[float], None]] = None,
    raise_on_error: bool = False,
    max_retries: int = MAX_RETRIES,
    max_backoff_seconds: float = MAX_BACKOFF_SECONDS,
    api_key: str | None = None,
) -> list[Paper]:
    """Search Semantic Scholar for papers matching a query.

    Uses Semantic Scholar's bulk-search endpoint with continuation-token
    pagination. The endpoint returns basic paper metadata and intentionally
    does not request nested references; detail retrieval remains available via
    :func:`get_paper_details`.

    Args:
        query: Free-text search query.
        max_results: Maximum number of results to retrieve.
        base_url: API base URL (injectable for testing).
        session: Optional requests.Session for connection reuse.
        raise_on_error: Raise terminal HTTP errors instead of returning the
            papers fetched before the error.

    Returns:
        List of Paper objects from the search results.

    Raises:
        requests.HTTPError: If the API returns a non-2xx status after retries.
    """
    http = session or requests.Session()
    resolved_api_key = api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY")
    if max_results <= 0:
        return []

    all_papers: list[Paper] = []

    try:
        continuation_token: str | None = None
        page_num = 0

        while len(all_papers) < max_results:
            page_size = min(S2_BULK_PAGE_SIZE, max_results - len(all_papers))
            page_num += 1

            params = {
                "query": query,
                "limit": page_size,
                "fields": S2_BULK_SEARCH_FIELDS,
            }
            if continuation_token:
                params["token"] = continuation_token

            logger.info(
                "S2 bulk page %d: fetching up to %d results (token=%s, target %d)",
                page_num,
                page_size,
                "present" if continuation_token else "initial",
                max_results,
            )

            try:
                response = _request_with_retry(
                    http,
                    f"{base_url.rstrip('/')}{S2_BULK_SEARCH_PATH}",
                    params,
                    max_retries=max_retries,
                    max_backoff_seconds=max_backoff_seconds,
                    api_key=resolved_api_key,
                    delay_override=delay_override,
                )
                result = response.json()
            except requests.RequestException as e:
                logger.warning("S2 bulk search stopped due to HTTP error: %s", e)
                if raise_on_error:
                    raise
                break

            page_papers = [_parse_s2_paper(item) for item in result.get("data", [])]

            if not page_papers:
                logger.info(
                    "S2 page %d: no more results (total fetched: %d)",
                    page_num, len(all_papers),
                )
                break

            remaining = max_results - len(all_papers)
            all_papers.extend(page_papers[:remaining])
            logger.info(
                "S2 page %d: fetched %d papers (total: %d)",
                page_num, min(len(page_papers), remaining), len(all_papers),
            )

            if len(all_papers) >= max_results:
                logger.info("S2: requested result limit reached (%d)", max_results)
                break

            next_token = result.get("token")
            if not next_token:
                logger.info(
                    "S2: bulk search complete (%d available results)",
                    result.get("total", len(all_papers)),
                )
                break

            if next_token == continuation_token:
                logger.error("S2: API returned a repeated continuation token; stopping")
                break
            continuation_token = str(next_token)
    finally:
        if session is None:
            http.close()

    logger.info("S2 search complete: %d total papers for query '%s'", len(all_papers), query[:80])
    return all_papers


def get_paper_details(
    paper_id: str,
    base_url: str = S2_API_URL,
    session: Optional[requests.Session] = None,
    max_retries: int = MAX_RETRIES,
    max_backoff_seconds: float = MAX_BACKOFF_SECONDS,
    api_key: str | None = None,
) -> Paper:
    """Retrieve detailed metadata for a single paper by ID.

    Args:
        paper_id: Semantic Scholar paper ID, DOI, or arXiv ID.
        base_url: API base URL (injectable for testing).
        session: Optional requests.Session for connection reuse.

    Returns:
        Paper object with full metadata.

    Raises:
        requests.HTTPError: If the API returns a non-2xx status (e.g. 404).
    """
    url = f"{base_url.rstrip('/')}/paper/{paper_id}"
    params = {"fields": PAPER_FIELDS}

    http = session or requests.Session()
    try:
        response = _request_with_retry(
            http,
            url,
            params,
            max_retries=max_retries,
            max_backoff_seconds=max_backoff_seconds,
            api_key=api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY"),
        )
    finally:
        if session is None:
            http.close()

    logger.debug("Retrieved paper details for %s", paper_id)
    return _parse_s2_paper(response.json())


def get_citations(
    paper_id: str,
    max_results: int = 100,
    base_url: str = S2_API_URL,
    session: Optional[requests.Session] = None,
    max_retries: int = MAX_RETRIES,
    max_backoff_seconds: float = MAX_BACKOFF_SECONDS,
    api_key: str | None = None,
) -> list[Citation]:
    """Retrieve papers that cite the given paper.

    Args:
        paper_id: Semantic Scholar paper ID.
        max_results: Maximum number of citations to retrieve.
        base_url: API base URL (injectable for testing).
        session: Optional requests.Session for connection reuse.

    Returns:
        List of Citation objects representing citing papers.

    Raises:
        requests.HTTPError: If the API returns a non-2xx status.
    """
    url = f"{base_url.rstrip('/')}/paper/{paper_id}/citations"
    params = {
        "limit": min(max_results, 100),
        "fields": CITATION_FIELDS,
    }

    http = session or requests.Session()
    try:
        response = _request_with_retry(
            http,
            url,
            params,
            max_retries=max_retries,
            max_backoff_seconds=max_backoff_seconds,
            api_key=api_key or os.environ.get("SEMANTIC_SCHOLAR_API_KEY"),
        )
    finally:
        if session is None:
            http.close()

    result = response.json()
    citations: list[Citation] = []
    target_id = f"s2:{paper_id}"

    for item in result.get("data", []):
        citing_paper = item.get("citingPaper", {})
        citing_id = citing_paper.get("paperId")
        if citing_id:
            context = item.get("contexts", [None])
            context_text = context[0] if isinstance(context, list) and context else None
            citations.append(
                Citation(
                    source_id=f"s2:{citing_id}",
                    target_id=target_id,
                    context=context_text,
                )
            )

    logger.info("Retrieved %d citations for paper %s", len(citations), paper_id)
    return citations
