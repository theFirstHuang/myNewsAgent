"""RIS format exporter for Zotero import."""

import logging
from pathlib import Path
from datetime import datetime
from typing import List
from ..fetchers.base import Paper

logger = logging.getLogger(__name__)


class RISExporter:
    """Exports papers to RIS format for Zotero."""

    def __init__(self, config):
        """Initialize RIS exporter.

        Args:
            config: Configuration object
        """
        self.config = config
        self.zotero_dir = Path(config.get('directories.zotero', 'outputs/zotero'))
        self.zotero_dir.mkdir(parents=True, exist_ok=True)

    def export_papers(self, papers: List[Paper]) -> Path:
        """Export papers to RIS file.

        Args:
            papers: List of papers

        Returns:
            Path to RIS file
        """
        logger.info(f"Exporting {len(papers)} papers to RIS format...")

        ris_content = self._generate_ris(papers)

        # Save RIS file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.zotero_dir / f"papers_{timestamp}.ris"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(ris_content)

        logger.info(f"RIS file saved to: {output_file}")
        return output_file

    def _generate_ris(self, papers: List[Paper]) -> str:
        """Generate RIS format content.

        Args:
            papers: List of papers

        Returns:
            RIS format string
        """
        ris_entries = []

        for paper in papers:
            entry = self._paper_to_ris(paper)
            ris_entries.append(entry)

        return "\n\n".join(ris_entries)

    def _paper_to_ris(self, paper: Paper) -> str:
        """Convert a single paper to RIS format.

        Args:
            paper: Paper object

        Returns:
            RIS format string for the paper
        """
        lines = [
            "TY  - JOUR",  # Journal Article
            f"TI  - {paper.title}",
        ]

        # Authors
        for author in paper.authors:
            lines.append(f"AU  - {author}")

        # Abstract
        if paper.abstract:
            lines.append(f"AB  - {paper.abstract}")

        # Publication date
        if paper.published:
            lines.append(f"PY  - {paper.published.year}")
            lines.append(f"DA  - {paper.published.strftime('%Y/%m/%d')}")

        # arXiv ID and URL
        lines.append(f"ID  - {paper.arxiv_id}")
        lines.append(f"UR  - https://arxiv.org/abs/{paper.short_id}")

        # PDF URL
        if paper.pdf_url:
            lines.append(f"L1  - {paper.pdf_url}")

        # Keywords from categories
        for category in paper.categories:
            lines.append(f"KW  - {category}")

        # Notes (relevance score and summary if available)
        if paper.relevance_score:
            lines.append(f"N1  - Relevance Score: {paper.relevance_score:.2f}")

        if paper.summary:
            summary_text = self._format_summary_for_notes(paper.summary)
            lines.append(f"N1  - {summary_text}")

        # End of record
        lines.append("ER  - ")

        return "\n".join(lines)

    def _format_summary_for_notes(self, summary: dict) -> str:
        """Format summary dictionary for RIS notes field.

        Args:
            summary: Summary dictionary

        Returns:
            Formatted string
        """
        parts = []

        if 'key_points' in summary and summary['key_points']:
            points = "; ".join(summary['key_points'][:3])  # First 3 points
            parts.append(f"Key Points: {points}")

        if 'relevance_reason' in summary:
            parts.append(f"Relevance: {summary['relevance_reason']}")

        return " | ".join(parts)
