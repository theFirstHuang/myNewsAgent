"""PDF download and conversion to Markdown using MinerU."""

import logging
import requests
import subprocess
from pathlib import Path
from typing import Optional, List
from concurrent.futures import ThreadPoolExecutor, as_completed
from tqdm import tqdm
from ..fetchers.base import Paper

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Downloads and converts PDFs to Markdown."""

    def __init__(self, config):
        """Initialize PDF processor.

        Args:
            config: Configuration object
        """
        self.config = config
        self.papers_dir = Path(config.get('directories.papers', 'data/papers'))
        self.markdown_dir = Path(config.get('directories.markdown', 'data/markdown'))
        self.papers_dir.mkdir(parents=True, exist_ok=True)
        self.markdown_dir.mkdir(parents=True, exist_ok=True)

        self.timeout = config.get('performance.request_timeout', 30)
        self.max_workers = config.get('performance.parallel_downloads', 5)
        self.mineru_enabled = config.get('processing.pdf_to_markdown.enabled', True)

    def download_paper(self, paper: Paper) -> Optional[Path]:
        """Download a single paper PDF.

        Args:
            paper: Paper object

        Returns:
            Path to downloaded PDF or None if failed
        """
        filename = f"{paper.short_id.replace('/', '_')}.pdf"
        filepath = self.papers_dir / filename

        # Skip if already exists
        if filepath.exists():
            logger.debug(f"PDF already exists: {filename}")
            paper.pdf_path = filepath
            return filepath

        try:
            logger.info(f"Downloading: {paper.title[:50]}...")

            response = requests.get(
                paper.pdf_url,
                timeout=self.timeout,
                headers={'User-Agent': 'Mozilla/5.0 (LLM Digest Agent)'}
            )
            response.raise_for_status()

            with open(filepath, 'wb') as f:
                f.write(response.content)

            logger.info(f"Downloaded: {filename}")
            paper.pdf_path = filepath
            return filepath

        except Exception as e:
            logger.error(f"Error downloading {paper.arxiv_id}: {e}")
            return None

    def download_batch(self, papers: List[Paper]) -> List[Paper]:
        """Download multiple papers in parallel.

        Args:
            papers: List of Paper objects

        Returns:
            List of papers with successful downloads
        """
        logger.info(f"Downloading {len(papers)} papers...")

        successful = []

        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_paper = {
                executor.submit(self.download_paper, paper): paper
                for paper in papers
            }

            for future in tqdm(
                as_completed(future_to_paper),
                total=len(papers),
                desc="Downloading PDFs"
            ):
                paper = future_to_paper[future]
                try:
                    result = future.result()
                    if result:
                        successful.append(paper)
                except Exception as e:
                    logger.error(f"Download failed for {paper.arxiv_id}: {e}")

        logger.info(f"Successfully downloaded {len(successful)}/{len(papers)} papers")
        return successful

    def convert_to_markdown(self, paper: Paper) -> Optional[Path]:
        """Convert PDF to Markdown using MinerU.

        Args:
            paper: Paper object with pdf_path set

        Returns:
            Path to markdown file or None if failed
        """
        if not self.mineru_enabled:
            logger.debug("MinerU conversion disabled")
            return None

        if not paper.pdf_path or not paper.pdf_path.exists():
            logger.warning(f"PDF not found for {paper.arxiv_id}")
            return None

        markdown_file = self.markdown_dir / f"{paper.short_id}.md"

        # Skip if already converted
        if markdown_file.exists():
            logger.debug(f"Markdown already exists: {markdown_file.name}")
            paper.markdown_path = markdown_file
            return markdown_file

        try:
            logger.info(f"Converting to markdown: {paper.title[:50]}...")

            # Run MinerU command
            # Note: MinerU syntax may vary, adjust as needed
            cmd = [
                "mineru",
                "pdf",
                str(paper.pdf_path),
                "-o", str(markdown_file)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=120  # 2 minutes timeout
            )

            if result.returncode == 0 and markdown_file.exists():
                logger.info(f"Converted: {markdown_file.name}")
                paper.markdown_path = markdown_file
                return markdown_file
            else:
                logger.error(
                    f"MinerU conversion failed for {paper.arxiv_id}: "
                    f"{result.stderr}"
                )
                return None

        except subprocess.TimeoutExpired:
            logger.error(f"MinerU timeout for {paper.arxiv_id}")
            return None
        except FileNotFoundError:
            logger.error(
                "MinerU not found. Please install: pip install mineru\n"
                "Or disable PDF conversion in config.yaml"
            )
            return None
        except Exception as e:
            logger.error(f"Error converting {paper.arxiv_id}: {e}")
            return None

    def convert_batch(self, papers: List[Paper]) -> List[Paper]:
        """Convert multiple papers to markdown.

        Args:
            papers: List of papers with PDFs downloaded

        Returns:
            List of papers with successful conversions
        """
        logger.info(f"Converting {len(papers)} papers to markdown...")

        successful = []

        for paper in tqdm(papers, desc="Converting to Markdown"):
            try:
                result = self.convert_to_markdown(paper)
                if result:
                    successful.append(paper)
            except Exception as e:
                logger.error(f"Conversion failed for {paper.arxiv_id}: {e}")

        logger.info(f"Successfully converted {len(successful)}/{len(papers)} papers")
        return successful

    def read_markdown(self, paper: Paper) -> Optional[str]:
        """Read converted markdown content.

        Args:
            paper: Paper with markdown_path set

        Returns:
            Markdown content or None
        """
        if not paper.markdown_path or not paper.markdown_path.exists():
            logger.warning(f"Markdown not found for {paper.arxiv_id}")
            return None

        try:
            with open(paper.markdown_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading markdown for {paper.arxiv_id}: {e}")
            return None
