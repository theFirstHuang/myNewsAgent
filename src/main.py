"""Main entry point for LLM News Digest Agent."""

import sys
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import Config
from src.utils.logger import setup_logger
from src.fetchers import ArxivFetcher, HuggingFaceFetcher
from src.analyzers import RelevanceAnalyzer
from src.processors import PDFProcessor
from src.summarizers import LLMSummarizer
from src.generators import HTMLGenerator, RISExporter
from src.notifiers import EmailSender

logger = logging.getLogger(__name__)


def main():
    """Main workflow."""
    try:
        print("=" * 60)
        print("🤖 LLM News Digest Agent")
        print("=" * 60)
        print()

        # Load configuration
        print("📋 Loading configuration...")
        config = Config("config.yaml")

        # Setup logging
        log_config = config.config.get('logging', {})
        setup_logger(
            level=log_config.get('level', 'INFO'),
            log_file=log_config.get('file', 'logs/digest.log'),
            format_style=log_config.get('format', 'detailed')
        )

        logger.info("="* 60)
        logger.info("Starting LLM News Digest Agent")
        logger.info("=" * 60)

        # Step 1: Fetch papers
        print("\n📚 Step 1/7: Fetching papers from sources...")
        all_papers = []

        if config.get('sources.arxiv.enabled', True):
            print("  - Fetching from arXiv...")
            arxiv_fetcher = ArxivFetcher(config)
            arxiv_papers = arxiv_fetcher.fetch_papers()
            all_papers.extend(arxiv_papers)
            print(f"    ✓ Found {len(arxiv_papers)} papers from arXiv")

        if config.get('sources.huggingface.enabled', True):
            print("  - Fetching from HuggingFace...")
            hf_fetcher = HuggingFaceFetcher(config)
            hf_papers = hf_fetcher.fetch_papers()
            all_papers.extend(hf_papers)
            print(f"    ✓ Found {len(hf_papers)} papers from HuggingFace")

        if not all_papers:
            print("⚠️  No papers found!")
            return

        print(f"\n  Total papers fetched: {len(all_papers)}")

        # Step 2: Analyze relevance
        print("\n🔍 Step 2/7: Analyzing paper relevance...")
        analyzer = RelevanceAnalyzer(config)
        threshold = config.get('processing.relevance_threshold', 0.7)
        relevant_papers, _ = analyzer.analyze_batch(all_papers, threshold=threshold)

        print(f"  ✓ {len(relevant_papers)} papers passed relevance filter (threshold: {threshold})")

        if not relevant_papers:
            print("⚠️  No relevant papers found!")
            return

        # Step 3: Download PDFs
        print("\n📥 Step 3/7: Downloading PDFs...")
        processor = PDFProcessor(config)

        # Limit downloads based on config
        max_to_process = config.get('processing.max_papers_to_process', 10)
        papers_to_download = relevant_papers[:max_to_process]

        if len(relevant_papers) > max_to_process:
            print(f"  ℹ️  Limiting to top {max_to_process} most relevant papers")

        downloaded_papers = processor.download_batch(papers_to_download)
        print(f"  ✓ Downloaded {len(downloaded_papers)} PDFs")

        # Step 4: Convert to Markdown
        if config.get('processing.pdf_to_markdown.enabled', True):
            print("\n📝 Step 4/7: Converting PDFs to Markdown...")
            converted_papers = processor.convert_batch(downloaded_papers)
            print(f"  ✓ Converted {len(converted_papers)} papers")
        else:
            print("\n⏭️  Step 4/7: Skipping PDF conversion (disabled in config)")
            converted_papers = downloaded_papers

        # Step 5: Generate summaries
        print("\n🧠 Step 5/7: Generating detailed summaries with LLM...")
        summarizer = LLMSummarizer(config)
        summarized_papers = summarizer.summarize_batch(converted_papers)
        print(f"  ✓ Generated {len(summarized_papers)} summaries")

        # Step 6: Generate reports
        print("\n📊 Step 6/7: Generating reports...")

        # HTML report
        html_gen = HTMLGenerator(config)
        html_file = html_gen.generate_report(summarized_papers)
        print(f"  ✓ HTML report: {html_file}")

        # RIS file for Zotero
        ris_file = None
        if config.get('processing.generate_ris', True):
            ris_exp = RISExporter(config)
            ris_file = ris_exp.export_papers(summarized_papers)
            print(f"  ✓ RIS file: {ris_file}")

        # Step 7: Send email
        print("\n📧 Step 7/7: Sending email...")
        sender = EmailSender(config)
        success = sender.send_report(html_file, ris_file)

        if success:
            print("  ✓ Email sent successfully!")
        else:
            print("  ✗ Failed to send email (check logs)")

        # Summary
        print("\n" + "=" * 60)
        print("✨ Digest Complete!")
        print("=" * 60)
        print(f"  Papers fetched:     {len(all_papers)}")
        print(f"  Relevant papers:    {len(relevant_papers)}")
        print(f"  Processed:          {len(summarized_papers)}")
        print(f"  Report saved:       {html_file}")
        if ris_file:
            print(f"  Zotero RIS:         {ris_file}")
        print("=" * 60)

        logger.info("Digest workflow completed successfully")

    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        logger.warning("Workflow interrupted by user")
        sys.exit(1)

    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        logger.error(f"Fatal error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
