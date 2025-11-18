"""Base classes for paper fetchers."""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class Paper:
    """Represents a research paper with metadata and summaries."""

    # Required fields
    title: str
    authors: List[str]
    abstract: str
    pdf_url: str
    arxiv_id: str
    published: datetime
    categories: List[str]

    # Optional fields
    primary_category: Optional[str] = None
    source: str = "arxiv"  # arxiv, huggingface, etc.
    relevance_score: Optional[float] = None
    summary: Optional[Dict[str, Any]] = None  # LLM-generated summary
    pdf_path: Optional[Path] = None  # Local PDF path
    markdown_path: Optional[Path] = None  # Converted markdown path

    # Metadata
    fetched_at: datetime = field(default_factory=datetime.now)
    processed: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """Convert paper to dictionary.

        Returns:
            Dictionary representation
        """
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        data['published'] = self.published.isoformat()
        data['fetched_at'] = self.fetched_at.isoformat()
        # Convert Path objects to strings
        if self.pdf_path:
            data['pdf_path'] = str(self.pdf_path)
        if self.markdown_path:
            data['markdown_path'] = str(self.markdown_path)
        return data

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Paper':
        """Create Paper from dictionary.

        Args:
            data: Dictionary with paper data

        Returns:
            Paper instance
        """
        # Convert ISO strings back to datetime
        if isinstance(data.get('published'), str):
            data['published'] = datetime.fromisoformat(data['published'])
        if isinstance(data.get('fetched_at'), str):
            data['fetched_at'] = datetime.fromisoformat(data['fetched_at'])

        # Convert strings back to Path
        if data.get('pdf_path'):
            data['pdf_path'] = Path(data['pdf_path'])
        if data.get('markdown_path'):
            data['markdown_path'] = Path(data['markdown_path'])

        return cls(**data)

    @property
    def short_id(self) -> str:
        """Get short arXiv ID without version.

        Returns:
            Short ID (e.g., '2401.12345')
        """
        # Remove version suffix like 'v1', 'v2'
        return self.arxiv_id.split('v')[0] if 'v' in self.arxiv_id else self.arxiv_id

    @property
    def authors_str(self) -> str:
        """Get formatted author string.

        Returns:
            Comma-separated author names
        """
        if len(self.authors) == 0:
            return "Unknown"
        elif len(self.authors) == 1:
            return self.authors[0]
        elif len(self.authors) == 2:
            return f"{self.authors[0]} and {self.authors[1]}"
        else:
            return f"{self.authors[0]} et al."

    @property
    def published_str(self) -> str:
        """Get formatted publication date.

        Returns:
            Date string (e.g., 'Jan 15, 2024')
        """
        return self.published.strftime("%b %d, %Y")

    def __repr__(self) -> str:
        """String representation."""
        return (
            f"Paper(id={self.short_id}, title='{self.title[:50]}...', "
            f"relevance={self.relevance_score})"
        )


class BaseFetcher(ABC):
    """Abstract base class for paper fetchers."""

    def __init__(self, config):
        """Initialize fetcher.

        Args:
            config: Configuration object
        """
        self.config = config

    @abstractmethod
    def fetch_papers(self) -> List[Paper]:
        """Fetch papers from source.

        Returns:
            List of Paper objects
        """
        pass

    def filter_by_date(
        self,
        papers: List[Paper],
        days_lookback: int
    ) -> List[Paper]:
        """Filter papers by publication date.

        Args:
            papers: List of papers
            days_lookback: Only keep papers from last N days

        Returns:
            Filtered list of papers
        """
        from datetime import timedelta

        cutoff_date = datetime.now() - timedelta(days=days_lookback)
        return [p for p in papers if p.published >= cutoff_date]

    def deduplicate(self, papers: List[Paper]) -> List[Paper]:
        """Remove duplicate papers by arxiv_id.

        Args:
            papers: List of papers

        Returns:
            Deduplicated list
        """
        seen = set()
        unique_papers = []

        for paper in papers:
            if paper.short_id not in seen:
                seen.add(paper.short_id)
                unique_papers.append(paper)

        return unique_papers
