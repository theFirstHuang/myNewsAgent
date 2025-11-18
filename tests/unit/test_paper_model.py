"""Tests for Paper data model."""

import pytest
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, 'src')
from fetchers.base import Paper


class TestPaperModel:
    """Test Paper data class."""

    def test_paper_creation(self):
        """Test creating a Paper object."""
        paper = Paper(
            title="Test Paper",
            authors=["Author 1", "Author 2"],
            abstract="This is a test abstract.",
            pdf_url="https://arxiv.org/pdf/2401.12345v1",
            arxiv_id="2401.12345v1",
            published=datetime(2024, 1, 15),
            categories=["cs.CL", "cs.AI"]
        )

        assert paper.title == "Test Paper"
        assert len(paper.authors) == 2
        assert paper.short_id == "2401.12345"

    def test_paper_short_id(self):
        """Test short_id property."""
        paper = Paper(
            title="Test",
            authors=["Author"],
            abstract="Abstract",
            pdf_url="url",
            arxiv_id="2401.12345v2",
            published=datetime.now(),
            categories=["cs.CL"]
        )

        assert paper.short_id == "2401.12345"

    def test_paper_authors_str(self):
        """Test authors_str formatting."""
        # Single author
        paper1 = Paper(
            title="Test",
            authors=["Alice"],
            abstract="Abstract",
            pdf_url="url",
            arxiv_id="2401.12345",
            published=datetime.now(),
            categories=["cs.CL"]
        )
        assert paper1.authors_str == "Alice"

        # Two authors
        paper2 = Paper(
            title="Test",
            authors=["Alice", "Bob"],
            abstract="Abstract",
            pdf_url="url",
            arxiv_id="2401.12345",
            published=datetime.now(),
            categories=["cs.CL"]
        )
        assert paper2.authors_str == "Alice and Bob"

        # Three or more authors
        paper3 = Paper(
            title="Test",
            authors=["Alice", "Bob", "Charlie"],
            abstract="Abstract",
            pdf_url="url",
            arxiv_id="2401.12345",
            published=datetime.now(),
            categories=["cs.CL"]
        )
        assert paper3.authors_str == "Alice et al."

    def test_paper_to_dict(self):
        """Test converting Paper to dict."""
        paper = Paper(
            title="Test Paper",
            authors=["Author"],
            abstract="Abstract",
            pdf_url="https://arxiv.org/pdf/2401.12345",
            arxiv_id="2401.12345",
            published=datetime(2024, 1, 15, 10, 30),
            categories=["cs.CL"]
        )

        paper_dict = paper.to_dict()

        assert paper_dict['title'] == "Test Paper"
        assert paper_dict['arxiv_id'] == "2401.12345"
        assert isinstance(paper_dict['published'], str)
        assert '2024-01-15' in paper_dict['published']

    def test_paper_from_dict(self):
        """Test creating Paper from dict."""
        paper_dict = {
            'title': "Test Paper",
            'authors': ["Author"],
            'abstract': "Abstract",
            'pdf_url': "https://arxiv.org/pdf/2401.12345",
            'arxiv_id': "2401.12345",
            'published': "2024-01-15T10:30:00",
            'categories': ["cs.CL"],
            'source': 'arxiv',
            'fetched_at': datetime.now().isoformat()
        }

        paper = Paper.from_dict(paper_dict)

        assert paper.title == "Test Paper"
        assert isinstance(paper.published, datetime)
        assert paper.published.year == 2024
