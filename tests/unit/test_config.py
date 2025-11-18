"""Tests for configuration management."""

import pytest
import tempfile
import os
from pathlib import Path
import yaml


class TestConfig:
    """Test Config class."""

    def test_config_structure(self):
        """Test config file structure is valid."""
        config_path = Path("config.yaml.example")
        assert config_path.exists(), "config.yaml.example not found"

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Check required top-level keys
        assert 'research_profile' in config
        assert 'sources' in config
        assert 'llm' in config
        assert 'email' in config
        assert 'processing' in config
        assert 'directories' in config

    def test_env_example_exists(self):
        """Test .env.example file exists."""
        env_path = Path(".env.example")
        assert env_path.exists(), ".env.example not found"

        with open(env_path, 'r') as f:
            content = f.read()

        # Check for required env vars
        assert 'OPENAI_API_KEY' in content
        assert 'GMAIL_APP_PASSWORD' in content

    def test_research_profile_example_exists(self):
        """Test research profile example exists."""
        profile_path = Path("my_research.md.example")
        assert profile_path.exists(), "my_research.md.example not found"

        with open(profile_path, 'r') as f:
            content = f.read()

        # Should contain research topics
        assert len(content) > 100
        assert 'LLM' in content or 'Large Language' in content

    def test_get_config_value(self):
        """Test config value retrieval."""
        config_path = Path("config.yaml.example")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        # Test nested access
        assert config['llm']['provider'] == 'openai'
        assert 'cs.CL' in config['sources']['arxiv']['categories']

    def test_directory_structure(self):
        """Test all required directories are defined."""
        config_path = Path("config.yaml.example")

        with open(config_path, 'r') as f:
            config = yaml.safe_load(f)

        dirs = config['directories']
        required_dirs = ['data', 'papers', 'outputs', 'logs']

        for dir_key in required_dirs:
            assert dir_key in dirs, f"Missing directory config: {dir_key}"
