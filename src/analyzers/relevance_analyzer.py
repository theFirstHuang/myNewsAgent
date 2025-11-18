"""Relevance analysis using LLM."""

import logging
from typing import List, Tuple
from openai import OpenAI
from ..fetchers.base import Paper

logger = logging.getLogger(__name__)


class RelevanceAnalyzer:
    """Analyzes paper relevance using LLM."""

    def __init__(self, config):
        """Initialize analyzer.

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
        self.research_profile = config.research_profile

    def analyze_batch(
        self,
        papers: List[Paper],
        threshold: float = 0.7
    ) -> Tuple[List[Paper], List[Paper]]:
        """Analyze relevance for a batch of papers.

        Args:
            papers: List of papers to analyze
            threshold: Minimum relevance score (0-1)

        Returns:
            Tuple of (relevant_papers, irrelevant_papers)
        """
        logger.info(f"Analyzing relevance for {len(papers)} papers...")

        relevant = []
        irrelevant = []

        for i, paper in enumerate(papers, 1):
            try:
                score, reason = self.analyze_single(paper)
                paper.relevance_score = score

                if score >= threshold:
                    relevant.append(paper)
                    logger.info(
                        f"[{i}/{len(papers)}] ✓ Relevant ({score:.2f}): {paper.title[:60]}..."
                    )
                else:
                    irrelevant.append(paper)
                    logger.debug(
                        f"[{i}/{len(papers)}] ✗ Not relevant ({score:.2f}): {paper.title[:60]}..."
                    )

            except Exception as e:
                logger.error(f"Error analyzing paper {paper.arxiv_id}: {e}")
                paper.relevance_score = 0.5  # Default score on error
                irrelevant.append(paper)

        logger.info(
            f"Relevance analysis complete: {len(relevant)} relevant, "
            f"{len(irrelevant)} filtered out"
        )

        # Sort by relevance score (descending)
        relevant.sort(key=lambda p: p.relevance_score or 0, reverse=True)

        return relevant, irrelevant

    def analyze_single(self, paper: Paper) -> Tuple[float, str]:
        """Analyze relevance of a single paper.

        Args:
            paper: Paper to analyze

        Returns:
            Tuple of (relevance_score, reason)
        """
        prompt = self._build_prompt(paper)

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": (
                            "You are a research assistant that evaluates paper relevance. "
                            "Respond with a JSON object containing 'score' (0-1) and 'reason' (brief explanation)."
                        )
                    },
                    {"role": "user", "content": prompt}
                ],
                temperature=self.temperature,
                max_tokens=300,
                response_format={"type": "json_object"}
            )

            import json
            result = json.loads(response.choices[0].message.content)
            score = float(result.get('score', 0.5))
            reason = result.get('reason', 'No reason provided')

            return score, reason

        except Exception as e:
            logger.error(f"LLM API error: {e}")
            return 0.5, "Error during analysis"

    def _build_prompt(self, paper: Paper) -> str:
        """Build analysis prompt.

        Args:
            paper: Paper to analyze

        Returns:
            Prompt string
        """
        return f"""# Research Profile
{self.research_profile}

---

# Paper to Evaluate

**Title:** {paper.title}

**Authors:** {paper.authors_str}

**Abstract:** {paper.abstract}

**Categories:** {', '.join(paper.categories)}

---

# Task

Evaluate how relevant this paper is to my research interests (described above).

Provide:
1. A relevance score from 0 to 1 (0=not relevant, 1=highly relevant)
2. A brief reason (1-2 sentences)

Respond in JSON format:
{{
  "score": 0.85,
  "reason": "This paper directly addresses..."
}}
"""
