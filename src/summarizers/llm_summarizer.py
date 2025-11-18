"""LLM-based paper summarization."""

import logging
import json
from typing import Dict, Any, List
from openai import OpenAI
from ..fetchers.base import Paper

logger = logging.getLogger(__name__)


class LLMSummarizer:
    """Generates detailed paper summaries using LLM."""

    def __init__(self, config):
        """Initialize summarizer.

        Args:
            config: Configuration object
        """
        self.config = config
        llm_config = config.llm_config

        if llm_config['provider'] == 'openai':
            self.client = OpenAI(api_key=llm_config['api_key'])
        else:
            raise ValueError(f"Unsupported LLM provider: {llm_config['provider']}")

        self.model = llm_config['model']
        self.temperature = llm_config['temperature']
        self.max_tokens = llm_config['max_tokens']
        self.research_profile = config.research_profile

    def summarize_batch(self, papers: List[Paper]) -> List[Paper]:
        """Generate summaries for multiple papers.

        Args:
            papers: List of papers

        Returns:
            List of papers with summaries added
        """
        logger.info(f"Generating summaries for {len(papers)} papers...")

        for i, paper in enumerate(papers, 1):
            try:
                logger.info(f"[{i}/{len(papers)}] Summarizing: {paper.title[:50]}...")
                summary = self.summarize_single(paper)
                paper.summary = summary
                paper.processed = True

            except Exception as e:
                logger.error(f"Error summarizing {paper.arxiv_id}: {e}")
                paper.summary = self._create_fallback_summary(paper)

        logger.info("All summaries generated")
        return papers

    def summarize_single(self, paper: Paper) -> Dict[str, Any]:
        """Generate detailed summary for a single paper.

        Args:
            paper: Paper object

        Returns:
            Summary dictionary
        """
        # Use markdown content if available, otherwise use abstract
        content = paper.abstract
        if paper.markdown_path and paper.markdown_path.exists():
            try:
                with open(paper.markdown_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    # Limit length to avoid token limits
                    if len(content) > 20000:
                        content = content[:20000] + "\n\n[Content truncated...]"
            except Exception as e:
                logger.warning(f"Error reading markdown, using abstract: {e}")

        prompt = self._build_summary_prompt(paper, content)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are an expert research assistant specializing in LLM and AI research. "
                            "Provide detailed, insightful paper summaries in JSON format."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                response_format={"type": "json_object"}
            )

            summary = json.loads(response.choices[0].message.content)
            return summary

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return self._create_fallback_summary(paper)

    def _build_summary_prompt(self, paper: Paper, content: str) -> str:
        """Build summarization prompt.

        Args:
            paper: Paper object
            content: Paper content (markdown or abstract)

        Returns:
            Prompt string
        """
        return f"""# My Research Interests
{self.research_profile}

---

# Paper to Summarize

**Title:** {paper.title}

**Authors:** {paper.authors_str}

**Published:** {paper.published_str}

**Categories:** {', '.join(paper.categories)}

**Content:**
{content}

---

# Task

Provide a detailed, technical summary of this paper that helps me quickly understand:

1. **Key Contributions** (3-5 bullet points): Main innovations and findings
2. **Methodology**: How did they achieve their results?
3. **Results & Performance**: Key numbers, benchmarks, improvements
4. **Relevance to My Research**: Why this matters to me specifically (given my research interests)
5. **Limitations**: Any caveats or weaknesses mentioned
6. **Future Work**: What's next according to the authors

**IMPORTANT:**
- Be specific and technical, not vague or generic
- Include numbers, metrics, and concrete details
- Focus on novelty and practical implications
- Keep it concise but comprehensive

Respond in JSON format:
{{
  "key_points": ["Point 1", "Point 2", ...],
  "methodology": "Description...",
  "results": "Key results...",
  "relevance_reason": "Why relevant...",
  "limitations": "Limitations...",
  "future_work": "Future directions..."
}}
"""

    def _create_fallback_summary(self, paper: Paper) -> Dict[str, Any]:
        """Create basic summary when LLM fails.

        Args:
            paper: Paper object

        Returns:
            Basic summary dict
        """
        return {
            "key_points": [
                "Summary generation failed",
                "Please read the abstract manually"
            ],
            "methodology": "Not available",
            "results": "Not available",
            "relevance_reason": "Could not analyze relevance",
            "limitations": "Not available",
            "future_work": "Not available"
        }
