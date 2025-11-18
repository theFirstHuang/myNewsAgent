"""HuggingFace Daily Papers fetcher."""

import requests
import logging
from datetime import datetime
from typing import List
from bs4 import BeautifulSoup
from .base import BaseFetcher, Paper

logger = logging.getLogger(__name__)


class HuggingFaceFetcher(BaseFetcher):
    """Fetches papers from HuggingFace Daily Papers."""

    def __init__(self, config):
        """Initialize HuggingFace fetcher.

        Args:
            config: Configuration object
        """
        super().__init__(config)
        self.enabled = config.get('sources.huggingface.enabled', True)
        self.base_url = config.get(
            'sources.huggingface.url',
            'https://huggingface.co/papers'
        )
        self.max_results = config.get('sources.huggingface.max_results', 15)
        self.timeout = config.get('performance.request_timeout', 30)

    def fetch_papers(self) -> List[Paper]:
        """Fetch trending papers from HuggingFace.

        Returns:
            List of Paper objects
        """
        if not self.enabled:
            logger.info("HuggingFace fetcher disabled in config")
            return []

        logger.info("Fetching papers from HuggingFace Daily Papers")

        try:
            response = requests.get(
                self.base_url,
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (LLM Digest Agent)'}
            )
            response.raise_for_status()

            papers = self._parse_html(response.text)
            logger.info(f"Found {len(papers)} papers from HuggingFace")

            return papers

        except requests.RequestException as e:
            logger.error(f"Error fetching HuggingFace papers: {e}", exc_info=True)
            return []
        except Exception as e:
            logger.error(f"Unexpected error parsing HuggingFace: {e}", exc_info=True)
            return []

    def _parse_html(self, html_content: str) -> List[Paper]:
        """Parse HTML to extract paper information.

        Args:
            html_content: HTML content

        Returns:
            List of Paper objects

        Note:
            This is a basic parser. HuggingFace's HTML structure may change,
            requiring updates to this method. Consider using their API if available.
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        papers = []

        # Find paper cards (structure may vary)
        # This is a simplified parser - adjust selectors based on actual HTML
        article_elements = soup.find_all('article', limit=self.max_results)

        if not article_elements:
            # Try alternative structure
            article_elements = soup.find_all(
                'div',
                class_=lambda x: x and 'paper' in x.lower(),
                limit=self.max_results
            )

        for elem in article_elements:
            try:
                paper = self._parse_article_element(elem)
                if paper:
                    papers.append(paper)
            except Exception as e:
                logger.warning(f"Error parsing article element: {e}")
                continue

        return papers

    def _parse_article_element(self, elem) -> Paper:
        """Parse a single article element.

        Args:
            elem: BeautifulSoup element

        Returns:
            Paper object or None
        """
        # Extract title
        title_elem = elem.find('h3') or elem.find('h2') or elem.find(['a', 'span'])
        if not title_elem:
            return None

        title = title_elem.get_text(strip=True)

        # Extract arXiv link
        arxiv_link = None
        arxiv_id = None

        links = elem.find_all('a')
        for link in links:
            href = link.get('href', '')
            if 'arxiv.org' in href:
                arxiv_link = href
                # Extract ID from URL
                parts = href.rstrip('/').split('/')
                if parts:
                    arxiv_id = parts[-1]
                break

        if not arxiv_id:
            logger.debug(f"No arXiv ID found for paper: {title}")
            # Generate a temporary ID
            arxiv_id = f"hf_{hash(title) % 1000000}"

        # Try to extract abstract (may not always be available)
        abstract_elem = elem.find('p')
        abstract = abstract_elem.get_text(strip=True) if abstract_elem else title

        # Try to extract authors (often not available on HuggingFace)
        authors = ["Unknown"]
        author_elem = elem.find(class_=lambda x: x and 'author' in x.lower())
        if author_elem:
            authors = [author_elem.get_text(strip=True)]

        # Create Paper object
        paper = Paper(
            title=title,
            authors=authors,
            abstract=abstract,
            pdf_url=arxiv_link or self.base_url,
            arxiv_id=arxiv_id,
            published=datetime.now(),  # HuggingFace doesn't always show date
            categories=["huggingface"],
            primary_category="huggingface",
            source="huggingface"
        )

        return paper
