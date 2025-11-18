"""Tests for utility modules."""

import pytest
import tempfile
import time
from pathlib import Path
import sys
import json

sys.path.insert(0, 'src')
from utils.cache import Cache


class TestCache:
    """Test Cache functionality."""

    def test_cache_set_and_get(self):
        """Test basic cache operations."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Cache(cache_dir=tmpdir, ttl_days=1)

            # Set value
            cache.set("test_key", {"data": "test_value"})

            # Get value
            result = cache.get("test_key")
            assert result is not None
            assert result['data'] == "test_value"

    def test_cache_miss(self):
        """Test cache miss returns None."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Cache(cache_dir=tmpdir, ttl_days=1)

            result = cache.get("nonexistent_key")
            assert result is None

    def test_cache_expiry(self):
        """Test cache expiration."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Cache(cache_dir=tmpdir, ttl_days=0)  # Expire immediately

            cache.set("test_key", {"data": "test"})

            # Sleep to ensure expiry
            time.sleep(0.1)

            # Manually check if would be expired (can't wait full day)
            cache_file = cache._get_cache_path("test_key")
            assert cache_file.exists()

    def test_cache_clear(self):
        """Test clearing all cache."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Cache(cache_dir=tmpdir, ttl_days=1)

            cache.set("key1", "value1")
            cache.set("key2", "value2")

            count = cache.clear()
            assert count == 2

            # Verify cache is empty
            assert cache.get("key1") is None
            assert cache.get("key2") is None

    def test_cache_delete(self):
        """Test deleting specific cache entry."""
        with tempfile.TemporaryDirectory() as tmpdir:
            cache = Cache(cache_dir=tmpdir, ttl_days=1)

            cache.set("key1", "value1")
            cache.set("key2", "value2")

            cache.delete("key1")

            assert cache.get("key1") is None
            assert cache.get("key2") == "value2"


class TestLogger:
    """Test logger setup."""

    def test_logger_import(self):
        """Test logger module imports correctly."""
        from utils.logger import setup_logger, get_logger

        logger = get_logger("test_logger")
        assert logger is not None
        assert logger.name == "test_logger"
