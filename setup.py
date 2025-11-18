"""Setup script for LLM News Digest Agent."""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding="utf-8") if readme_file.exists() else ""

setup(
    name="llm-news-digest-agent",
    version="1.0.0",
    description="Automated LLM research paper digest with email reports",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Your Name",
    author_email="your.email@example.com",
    url="https://github.com/yourusername/myNewsAgent",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10,<3.14",
    install_requires=[
        "arxiv>=2.3.1",
        "openai>=1.12.0",
        "pyyaml>=6.0.1",
        "jinja2>=3.1.3",
        "python-dotenv>=1.0.1",
        "feedparser>=6.0.11",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.3",
        "schedule>=1.2.1",
        "python-dateutil>=2.8.2",
        "tqdm>=4.66.1",
    ],
    extras_require={
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "mypy>=1.8.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "llm-digest=main:main",
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
