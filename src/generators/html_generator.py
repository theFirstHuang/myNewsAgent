"""HTML email report generation."""

import logging
from datetime import datetime
from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader, select_autoescape
from ..fetchers.base import Paper

logger = logging.getLogger(__name__)


class HTMLGenerator:
    """Generates HTML email reports."""

    def __init__(self, config):
        """Initialize HTML generator.

        Args:
            config: Configuration object
        """
        self.config = config
        self.template_name = config.get('email.template', 'modern')
        self.reports_dir = Path(config.get('directories.reports', 'outputs/reports'))
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        # Setup Jinja2 environment
        template_dir = Path(__file__).parent.parent.parent / 'templates'
        self.env = Environment(
            loader=FileSystemLoader(str(template_dir)),
            autoescape=select_autoescape(['html', 'xml'])
        )

        # Add custom filters
        self.env.filters['format_date'] = self._format_date
        self.env.filters['truncate_text'] = self._truncate_text

    def generate_report(
        self,
        papers: List[Paper],
        date_range: str = None
    ) -> Path:
        """Generate HTML email report.

        Args:
            papers: List of papers with summaries
            date_range: Date range string (e.g., "Jan 15 - Jan 22, 2024")

        Returns:
            Path to generated HTML file
        """
        logger.info(f"Generating HTML report with {len(papers)} papers...")

        if not date_range:
            date_range = self._get_date_range(papers)

        # Prepare template data
        template_data = self._prepare_template_data(papers, date_range)

        # Render template
        template_file = f"email_{self.template_name}.html"
        try:
            template = self.env.get_template(template_file)
        except Exception as e:
            logger.error(f"Template not found: {template_file}, using 'modern'")
            template = self.env.get_template("email_modern.html")

        html_content = template.render(**template_data)

        # Save report
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_file = self.reports_dir / f"digest_{timestamp}.html"

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        logger.info(f"Report saved to: {output_file}")
        return output_file

    def _prepare_template_data(
        self,
        papers: List[Paper],
        date_range: str
    ) -> dict:
        """Prepare data for template rendering.

        Args:
            papers: List of papers
            date_range: Date range string

        Returns:
            Dictionary with template data
        """
        # Count highly relevant papers (score >= 0.8)
        relevant_count = sum(
            1 for p in papers
            if p.relevance_score and p.relevance_score >= 0.8
        )

        # Prepare paper data for template
        papers_data = []
        for paper in papers:
            paper_dict = {
                'title': paper.title,
                'authors': paper.authors_str,
                'abstract': paper.abstract,
                'arxiv_url': f"https://arxiv.org/abs/{paper.short_id}",
                'pdf_url': paper.pdf_url,
                'arxiv_id': paper.arxiv_id,
                'date': paper.published_str,
                'category': paper.primary_category or paper.categories[0],
                'relevance_score': paper.relevance_score or 0.5,
                'summary': paper.summary
            }
            papers_data.append(paper_dict)

        return {
            'date_range': date_range,
            'total_papers': len(papers),
            'relevant_papers': relevant_count,
            'papers': papers_data,
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

    def _get_date_range(self, papers: List[Paper]) -> str:
        """Get date range from papers.

        Args:
            papers: List of papers

        Returns:
            Date range string
        """
        if not papers:
            return datetime.now().strftime("%b %d, %Y")

        dates = [p.published for p in papers if p.published]
        if not dates:
            return datetime.now().strftime("%b %d, %Y")

        min_date = min(dates)
        max_date = max(dates)

        if min_date.date() == max_date.date():
            return min_date.strftime("%b %d, %Y")
        else:
            return f"{min_date.strftime('%b %d')} - {max_date.strftime('%b %d, %Y')}"

    @staticmethod
    def _format_date(dt: datetime) -> str:
        """Format datetime for display.

        Args:
            dt: Datetime object

        Returns:
            Formatted date string
        """
        if isinstance(dt, datetime):
            return dt.strftime("%b %d, %Y")
        return str(dt)

    @staticmethod
    def _truncate_text(text: str, length: int = 200) -> str:
        """Truncate text to length.

        Args:
            text: Text to truncate
            length: Maximum length

        Returns:
            Truncated text
        """
        if len(text) <= length:
            return text
        return text[:length].rsplit(' ', 1)[0] + '...'
