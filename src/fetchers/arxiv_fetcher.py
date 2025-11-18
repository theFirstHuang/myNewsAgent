"""arXiv paper fetcher using official API."""

import arxiv
import logging
from datetime import datetime, timedelta
from typing import List, Optional
from .base import BaseFetcher, Paper

logger = logging.getLogger(__name__)


class ArxivFetcher(BaseFetcher):
    """Fetches papers from arXiv API."""

    def __init__(self, config):
        """Initialize arXiv fetcher.

        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.enabled = config.get('sources.arxiv.enabled', True)
        self.categories = config.get('sources.arxiv.categories', ['cs.CL'])
        self.max_results = config.get('sources.arxiv.max_results', 30)
        self.days_lookback = config.get('sources.arxiv.days_lookback', 7)

    def fetch_papers(self) -> List[Paper]:
        """Fetch recent papers from arXiv.

        Returns:
            List of Paper objects
        """
        if not self.enabled:
            logger.info("arXiv fetcher disabled in config")
            return []

        logger.info(f"Fetching papers from arXiv categories: {self.categories}")

        all_papers = []

        for category in self.categories:
            try:
                papers = self._fetch_category(category)
                all_papers.extend(papers)
                logger.info(f"Found {len(papers)} papers in {category}")
            except Exception as e:
                logger.error(f"Error fetching {category}: {e}", exc_info=True)

        # Remove duplicates and filter by date
        unique_papers = self.deduplicate(all_papers)
        filtered_papers = self.filter_by_date(unique_papers, self.days_lookback)

        logger.info(
            f"Total papers after filtering: {len(filtered_papers)} "
            f"(from {len(all_papers)} raw)"
        )

        return filtered_papers

    def _fetch_category(self, category: str) -> List[Paper]:
        """Fetch papers from a specific arXiv category.

        Args:
            category: arXiv category (e.g., 'cs.CL')

        Returns:
            List of Paper objects
        """
        # Build search query
        search = arxiv.Search(
            query=f"cat:{category}",
            max_results=self.max_results,
            sort_by=arxiv.SortCriterion.SubmittedDate,
            sort_order=arxiv.SortOrder.Descending
        )

        papers = []

        try:
            for result in search.results():
                paper = self._convert_result(result)
                if paper:
                    papers.append(paper)

        except Exception as e:
            logger.error(f"Error processing arXiv results: {e}", exc_info=True)

        return papers

    def _convert_result(self, result: arxiv.Result) -> Optional[Paper]:
        """Convert arXiv Result to Paper object.

        Args:
            result: arXiv Result object

        Returns:
            Paper object or None if conversion fails
        """
        try:
            # Extract arXiv ID from entry_id (format: http://arxiv.org/abs/2401.12345v1)
            arxiv_id = result.entry_id.split('/')[-1]

            paper = Paper(
                title=result.title.strip(),
                authors=[author.name for author in result.authors],
                abstract=result.summary.strip(),
                pdf_url=result.pdf_url,
                arxiv_id=arxiv_id,
                published=result.published,
                categories=result.categories,
                primary_category=result.primary_category,
                source="arxiv"
            )

            return paper

        except Exception as e:
            logger.warning(f"Error converting arXiv result: {e}")
            return None

    def fetch_by_ids(self, arxiv_ids: List[str]) -> List[Paper]:
        """Fetch specific papers by arXiv IDs.

        Args:
            arxiv_ids: List of arXiv IDs

        Returns:
            List of Paper objects
        """
        logger.info(f"Fetching {len(arxiv_ids)} specific papers from arXiv")

        search = arxiv.Search(id_list=arxiv_ids)
        papers = []

        try:
            for result in search.results():
                paper = self._convert_result(result)
                if paper:
                    papers.append(paper)

        except Exception as e:
            logger.error(f"Error fetching papers by IDs: {e}", exc_info=True)

        return papers

    def search_by_query(self, query: str, max_results: int = 20) -> List[Paper]:
        """Search papers by custom query.

        Args:
            query: Search query string
            max_results: Maximum number of results

        Returns:
            List of Paper objects
        """
        logger.info(f"Searching arXiv with query: {query}")

        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance
        )

        papers = []

        try:
            for result in search.results():
                paper = self._convert_result(result)
                if paper:
                    papers.append(paper)

        except Exception as e:
            logger.error(f"Error searching arXiv: {e}", exc_info=True)

        logger.info(f"Found {len(papers)} papers for query")
        return papers
