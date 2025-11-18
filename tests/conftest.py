"""Pytest configuration and fixtures."""

import pytest
import sys
from pathlib import Path

# Add src to path for imports
src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))


@pytest.fixture
def sample_paper_data():
    """Sample paper data for testing."""
    from datetime import datetime

    return {
        'title': 'Sample LLM Research Paper',
        'authors': ['Alice Smith', 'Bob Johnson', 'Carol Williams'],
        'abstract': 'This paper presents a novel approach to fine-tuning large language models using reinforcement learning with human feedback.',
        'pdf_url': 'https://arxiv.org/pdf/2401.12345v1',
        'arxiv_id': '2401.12345v1',
        'published': datetime(2024, 1, 15, 10, 30),
        'categories': ['cs.CL', 'cs.AI', 'cs.LG'],
        'primary_category': 'cs.CL',
        'source': 'arxiv'
    }


@pytest.fixture
def sample_config_dict():
    """Sample configuration dictionary."""
    return {
        'research_profile': {
            'profile_file': 'my_research.md'
        },
        'sources': {
            'arxiv': {
                'enabled': True,
                'categories': ['cs.CL', 'cs.AI'],
                'max_results': 10,
                'days_lookback': 7
            }
        },
        'llm': {
            'provider': 'openai',
            'model': 'gpt-4o-mini',
            'temperature': 0.3
        },
        'email': {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'template': 'modern'
        },
        'processing': {
            'relevance_threshold': 0.7,
            'max_papers_to_process': 10
        },
        'directories': {
            'data': 'data',
            'papers': 'data/papers',
            'outputs': 'outputs'
        }
    }
