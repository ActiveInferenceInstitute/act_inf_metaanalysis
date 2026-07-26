"""Tests for Semantic Scholar Graph API client.

Uses pytest-httpserver to serve realistic S2 JSON responses locally.
Tests search, get_paper_details, and get_citations functions.
"""


import pytest
import requests
from pytest_httpserver import HTTPServer

from literature.semantic_scholar import (
    S2_BULK_SEARCH_FIELDS,
    S2_USER_AGENT,
    SemanticScholarRateLimitError,
    _retry_after_seconds,
    get_citations,
    get_paper_details,
    search_semantic_scholar,
)
from literature.models import Paper, Citation


# ---------------------------------------------------------------------------
# Sample Semantic Scholar API responses
# ---------------------------------------------------------------------------

SEARCH_RESPONSE = {
    "total": 2,
    "data": [
        {
            "paperId": "abc123",
            "title": "Active Inference: A Process Theory",
            "abstract": "This paper introduces active inference as a unified process theory for understanding perception, action, and learning.",
            "year": 2017,
            "authors": [
                {"authorId": "1234", "name": "Karl Friston"},
                {"authorId": "5678", "name": "Thomas Parr"},
            ],
            "externalIds": {
                "DOI": "10.1162/NECO_a_00912",
                "ArXiv": "1709.02341",
                "CorpusId": 99999,
            },
            "citationCount": 450,
            "venue": "Neural Computation",
            "isOpenAccess": True,
            "openAccessPdf": {
                "url": "https://arxiv.org/pdf/1709.02341.pdf",
                "status": "GREEN"
            },
        },
        {
            "paperId": "xyz789",
            "title": "The free-energy principle: a unified brain theory?",
            "abstract": "A free-energy principle for the brain is proposed.",
            "year": 2010,
            "authors": [
                {"authorId": "1234", "name": "Karl Friston"},
            ],
            "externalIds": {
                "DOI": "10.1038/nrn2787",
            },
            "citationCount": 3500,
            "venue": "Nature Reviews Neuroscience",
            "isOpenAccess": False,
            "openAccessPdf": None,
        },
    ],
}

PAPER_DETAILS_RESPONSE = {
    "paperId": "abc123",
    "title": "Active Inference: A Process Theory",
    "abstract": "This paper introduces active inference as a unified process theory.",
    "year": 2017,
    "authors": [
        {"authorId": "1234", "name": "Karl Friston"},
        {"authorId": "5678", "name": "Thomas Parr"},
        {"authorId": "9012", "name": "Giovanni Pezzulo"},
    ],
    "externalIds": {
        "DOI": "10.1162/NECO_a_00912",
        "ArXiv": "1709.02341",
    },
    "citationCount": 450,
    "venue": "Neural Computation",
    "references": [
        {"paperId": "def456"},
    ],
}

CITATIONS_RESPONSE = {
    "offset": 0,
    "data": [
        {
            "citingPaper": {
                "paperId": "cite001",
                "title": "Active Inference for Robot Control",
                "year": 2020,
                "authors": [{"name": "Pablo Lanillos"}],
                "externalIds": {"DOI": "10.1234/robot2020"},
            },
            "contexts": ["Building on the active inference framework (Friston et al., 2017)"],
        },
        {
            "citingPaper": {
                "paperId": "cite002",
                "title": "Bayesian Brain Hypothesis",
                "year": 2019,
                "authors": [{"name": "Anil Seth"}],
                "externalIds": {},
            },
            "contexts": None,
        },
    ],
}

EMPTY_SEARCH_RESPONSE = {
    "total": 0,
    "data": [],
}


# ---------------------------------------------------------------------------
# search_semantic_scholar tests
# ---------------------------------------------------------------------------


class TestSearchSemanticScholar:
    """Tests for the search function."""

    def test_search_returns_papers(self, httpserver: HTTPServer):
        """Search returns correctly parsed Paper objects."""
        httpserver.expect_request("/paper/search/bulk").respond_with_json(SEARCH_RESPONSE)

        papers = search_semantic_scholar(
            query="active inference",
            max_results=10,
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )

        assert len(papers) == 2
        assert isinstance(papers[0], Paper)
        assert papers[0].title == "Active Inference: A Process Theory"
        assert papers[0].s2_id == "abc123"
        assert papers[0].doi == "10.1162/NECO_a_00912"
        assert papers[0].arxiv_id == "1709.02341"
        assert papers[0].year == 2017
        assert papers[0].citation_count == 450
        assert papers[0].venue == "Neural Computation"
        assert papers[0].is_open_access is True
        assert papers[0].pdf_url == "https://arxiv.org/pdf/1709.02341.pdf"
        assert papers[0].full_text_source == "semantic_scholar"

        # Second paper is not open access
        assert papers[1].is_open_access is False
        assert papers[1].pdf_url is None
        assert papers[1].full_text_source is None

    def test_search_authors_parsed(self, httpserver: HTTPServer):
        """Authors are correctly parsed from search results."""
        httpserver.expect_request("/paper/search/bulk").respond_with_json(SEARCH_RESPONSE)

        papers = search_semantic_scholar(
            query="active inference",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )

        assert len(papers[0].authors) == 2
        assert papers[0].authors[0].name == "Karl Friston"
        assert papers[0].authors[1].name == "Thomas Parr"

    def test_bulk_search_does_not_require_nested_references(self, httpserver: HTTPServer):
        """Bulk search remains valid because nested references are detail-only."""
        httpserver.expect_request("/paper/search/bulk").respond_with_json(SEARCH_RESPONSE)

        papers = search_semantic_scholar(
            query="active inference",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )

        assert papers[0].references == []
        assert papers[1].references == []

    def test_search_empty_results(self, httpserver: HTTPServer):
        """Search with no results returns empty list."""
        httpserver.expect_request("/paper/search/bulk").respond_with_json(EMPTY_SEARCH_RESPONSE)

        papers = search_semantic_scholar(
            query="nonexistent topic xyz",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )

        assert papers == []

    def test_search_canonical_id(self, httpserver: HTTPServer):
        """Paper canonical_id uses DOI when available."""
        httpserver.expect_request("/paper/search/bulk").respond_with_json(SEARCH_RESPONSE)

        papers = search_semantic_scholar(
            query="active inference",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )

        assert papers[0].canonical_id == "doi:10.1162/NECO_a_00912"

    def test_search_http_error(self, httpserver: HTTPServer):
        """HTTP error after retries is swallowed and returns empty list."""
        httpserver.expect_request("/paper/search/bulk").respond_with_data(
            "Rate limited", status=429
        )

        papers = search_semantic_scholar(
            query="test",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )
        assert papers == []

    def test_search_with_session(self, httpserver: HTTPServer):
        """Search works with a provided session."""
        httpserver.expect_request("/paper/search/bulk").respond_with_json(SEARCH_RESPONSE)

        session = requests.Session()
        papers = search_semantic_scholar(
            query="test",
            base_url=httpserver.url_for(""),
            session=session,
            delay_override=lambda _: None,
        )
        session.close()

        assert len(papers) == 2

    def test_bulk_search_caps_provider_over_return(self, httpserver: HTTPServer):
        """The local result contract holds if the provider returns extra rows."""
        httpserver.expect_request(
            "/paper/search/bulk",
            query_string={"query": "test", "limit": "1", "fields": S2_BULK_SEARCH_FIELDS},
        ).respond_with_json(SEARCH_RESPONSE)

        papers = search_semantic_scholar(
            query="test",
            max_results=1,
            base_url=httpserver.url_for(""),
        )
        assert len(papers) == 1
        httpserver.check()

    def test_bulk_search_sends_documented_headers(self, httpserver: HTTPServer):
        """Requests include the API key and stable identification headers."""
        httpserver.expect_request(
            "/paper/search/bulk",
            headers={"x-api-key": "test-secret", "User-Agent": S2_USER_AGENT},
        ).respond_with_json(EMPTY_SEARCH_RESPONSE)

        search_semantic_scholar(
            query="test",
            base_url=httpserver.url_for(""),
            api_key="test-secret",
        )
        httpserver.check()

    def test_detail_parses_string_references(self, httpserver: HTTPServer):
        """The detail parser tolerates string reference identifiers."""
        response_with_string_refs = {
            "paperId": "str_ref_paper",
            "title": "Paper with string refs",
            "abstract": "Test abstract",
            "year": 2023,
            "authors": [{"name": "Test Author"}],
            "externalIds": {},
            "citationCount": 10,
            "venue": "Test Venue",
            "references": ["ref_string_id_1", "ref_string_id_2"],
        }
        httpserver.expect_request("/paper/str_ref_paper").respond_with_json(response_with_string_refs)

        paper = get_paper_details(
            paper_id="str_ref_paper",
            base_url=httpserver.url_for(""),
        )

        assert "s2:ref_string_id_1" in paper.references
        assert "s2:ref_string_id_2" in paper.references

    def test_search_null_fields(self, httpserver: HTTPServer):
        """Papers with null authors, references, etc. are handled."""
        response_with_nulls = {
            "total": 1,
            "data": [{
                "paperId": "null_paper",
                "title": "Paper with nulls",
                "abstract": None,
                "year": None,
                "authors": None,
                "externalIds": None,
                "citationCount": None,
                "venue": None,
            }],
        }
        httpserver.expect_request("/paper/search/bulk").respond_with_json(response_with_nulls)

        papers = search_semantic_scholar(
            query="test",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )

        assert len(papers) == 1
        assert papers[0].abstract == ""
        assert papers[0].authors == []
        assert papers[0].references == []
        assert papers[0].citation_count == 0
        assert papers[0].is_open_access is None
        assert papers[0].pdf_url is None


# ---------------------------------------------------------------------------
# get_paper_details tests
# ---------------------------------------------------------------------------


class TestGetPaperDetails:
    """Tests for the paper details function."""

    def test_get_details(self, httpserver: HTTPServer):
        """get_paper_details returns a fully populated Paper."""
        httpserver.expect_request("/paper/abc123").respond_with_json(
            PAPER_DETAILS_RESPONSE
        )

        paper = get_paper_details(
            paper_id="abc123",
            base_url=httpserver.url_for(""),
        )

        assert isinstance(paper, Paper)
        assert paper.title == "Active Inference: A Process Theory"
        assert paper.s2_id == "abc123"
        assert paper.doi == "10.1162/NECO_a_00912"
        assert paper.arxiv_id == "1709.02341"
        assert len(paper.authors) == 3
        assert paper.authors[2].name == "Giovanni Pezzulo"

    def test_get_details_references(self, httpserver: HTTPServer):
        """References from details endpoint are parsed."""
        httpserver.expect_request("/paper/abc123").respond_with_json(
            PAPER_DETAILS_RESPONSE
        )

        paper = get_paper_details(
            paper_id="abc123",
            base_url=httpserver.url_for(""),
        )

        assert "s2:def456" in paper.references

    def test_get_details_not_found(self, httpserver: HTTPServer):
        """404 response raises HTTPError."""
        httpserver.expect_request("/paper/nonexistent").respond_with_data(
            '{"error": "Paper not found"}', status=404
        )

        with pytest.raises(Exception):
            get_paper_details(
                paper_id="nonexistent",
                base_url=httpserver.url_for(""),
            )

    def test_get_details_with_session(self, httpserver: HTTPServer):
        """get_paper_details works with a provided session."""
        httpserver.expect_request("/paper/abc123").respond_with_json(
            PAPER_DETAILS_RESPONSE
        )

        session = requests.Session()
        paper = get_paper_details(
            paper_id="abc123",
            base_url=httpserver.url_for(""),
            session=session,
        )
        session.close()

        assert paper.title == "Active Inference: A Process Theory"


# ---------------------------------------------------------------------------
# get_citations tests
# ---------------------------------------------------------------------------


class TestGetCitations:
    """Tests for the citation retrieval function."""

    def test_get_citations(self, httpserver: HTTPServer):
        """get_citations returns Citation objects with correct source/target."""
        httpserver.expect_request("/paper/abc123/citations").respond_with_json(
            CITATIONS_RESPONSE
        )

        citations = get_citations(
            paper_id="abc123",
            base_url=httpserver.url_for(""),
        )

        assert len(citations) == 2
        assert isinstance(citations[0], Citation)
        assert citations[0].source_id == "s2:cite001"
        assert citations[0].target_id == "s2:abc123"

    def test_citation_context(self, httpserver: HTTPServer):
        """Citations include context text when available."""
        httpserver.expect_request("/paper/abc123/citations").respond_with_json(
            CITATIONS_RESPONSE
        )

        citations = get_citations(
            paper_id="abc123",
            base_url=httpserver.url_for(""),
        )

        assert "active inference framework" in citations[0].context.lower()
        assert citations[1].context is None

    def test_empty_citations(self, httpserver: HTTPServer):
        """Paper with no citations returns empty list."""
        httpserver.expect_request("/paper/lonely/citations").respond_with_json(
            {"offset": 0, "data": []}
        )

        citations = get_citations(
            paper_id="lonely",
            base_url=httpserver.url_for(""),
        )

        assert citations == []

    def test_citations_http_error(self, httpserver: HTTPServer):
        """HTTP error on citations endpoint raises exception."""
        httpserver.expect_request("/paper/bad/citations").respond_with_data(
            "Error", status=500
        )

        with pytest.raises(Exception):
            get_citations(
                paper_id="bad",
                base_url=httpserver.url_for(""),
                max_retries=0,
            )

    def test_citations_max_results(self, httpserver: HTTPServer):
        """max_results is passed to the API."""
        httpserver.expect_request("/paper/abc123/citations").respond_with_json(
            {"offset": 0, "data": []}
        )

        get_citations(
            paper_id="abc123",
            max_results=50,
            base_url=httpserver.url_for(""),
        )
        httpserver.check()

    def test_citations_with_session(self, httpserver: HTTPServer):
        """get_citations works with a provided session."""
        httpserver.expect_request("/paper/abc123/citations").respond_with_json(
            CITATIONS_RESPONSE
        )

        session = requests.Session()
        citations = get_citations(
            paper_id="abc123",
            base_url=httpserver.url_for(""),
            session=session,
        )
        session.close()

        assert len(citations) == 2



class TestS2PaginationAndRetry:
    """Tests for auto-pagination and retry logic."""

    def test_pagination(self, httpserver: HTTPServer):
        """search_semantic_scholar follows bulk continuation tokens."""
        # Page 1: 100 results and a continuation token.
        page1 = {
            "total": 150,
            "token": "next-page",
            "data": [{"paperId": f"id_{i}", "title": f"Paper {i}"} for i in range(100)],
        }
        # Page 2: 50 results (partial page)
        page2 = {
            "total": 150,
            "token": None,
            "data": [{"paperId": f"id_{i+100}", "title": f"Paper {i+100}"} for i in range(50)]
        }

        # Expect calls with a continuation token (order matters for client logic).
        httpserver.expect_request(
            "/paper/search/bulk",
            query_string={"query": "test", "limit": "150", "fields": S2_BULK_SEARCH_FIELDS}
        ).respond_with_json(page1)
        
        httpserver.expect_request(
            "/paper/search/bulk",
            query_string={"query": "test", "limit": "50", "token": "next-page", "fields": S2_BULK_SEARCH_FIELDS}
        ).respond_with_json(page2)

        papers = search_semantic_scholar(
            query="test",
            max_results=150,
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )
        assert len(papers) == 150
        assert papers[0].title == "Paper 0"
        assert papers[149].title == "Paper 149"

    def test_retry_on_429(self, httpserver: HTTPServer):
        """search retries on 429 Too Many Requests within the configured budget."""
        # Fail once with 429 then succeed
        httpserver.expect_ordered_request("/paper/search/bulk").respond_with_data("Rate Limit", status=429)
        httpserver.expect_ordered_request("/paper/search/bulk").respond_with_json(
            {"total": 1, "data": [{"paperId": "id_1", "title": "Success"}]}
        )

        papers = search_semantic_scholar(
            query="test",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )
        assert len(papers) == 1
        assert papers[0].title == "Success"

    def test_retry_on_transient_503(self, httpserver: HTTPServer):
        """search retries a transient server error and then succeeds."""
        httpserver.expect_ordered_request("/paper/search/bulk").respond_with_data(
            "Service unavailable", status=503
        )
        httpserver.expect_ordered_request("/paper/search/bulk").respond_with_json(
            {"total": 1, "data": [{"paperId": "id_503", "title": "Recovered"}]}
        )

        papers = search_semantic_scholar(
            query="test",
            base_url=httpserver.url_for(""),
            delay_override=lambda _: None,
        )
        assert [paper.title for paper in papers] == ["Recovered"]

    def test_rate_limit_error_is_structured_and_secret_safe(self, httpserver: HTTPServer):
        """A terminal 429 exposes diagnostics without exposing the API key."""
        for _ in range(4):
            httpserver.expect_ordered_request("/paper/search/bulk").respond_with_data(
                '{"message":"Too Many Requests"}',
                status=429,
                headers={"Retry-After": "0"},
            )

        with pytest.raises(SemanticScholarRateLimitError) as exc_info:
            search_semantic_scholar(
                query="test",
                base_url=httpserver.url_for(""),
                api_key="test-secret",
                max_retries=3,
                delay_override=lambda _: None,
                raise_on_error=True,
            )

        error = exc_info.value
        assert error.status_code == 429
        assert error.rate_limited is True
        assert error.api_key_configured is True
        assert error.attempts == 4
        assert error.retry_after == 0.0
        assert "test-secret" not in str(error)

    def test_retry_after_header_parser(self):
        assert _retry_after_seconds("2") == 2.0
        assert _retry_after_seconds("not-a-delay") is None
        assert _retry_after_seconds(None) is None
