"""Simple file-based caching utilities."""

import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Optional, Callable
import logging

logger = logging.getLogger(__name__)


class Cache:
    """Simple file-based cache for paper data."""

    def __init__(self, cache_dir: str = "data/cache", ttl_days: int = 7):
        """Initialize cache.

        Args:
            cache_dir: Directory to store cache files
            ttl_days: Time-to-live in days
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.ttl = timedelta(days=ttl_days)

    def _get_cache_path(self, key: str) -> Path:
        """Get cache file path for a key.

        Args:
            key: Cache key

        Returns:
            Path to cache file
        """
        # Hash the key to create a safe filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"

    def get(self, key: str) -> Optional[Any]:
        """Get cached value.

        Args:
            key: Cache key

        Returns:
            Cached value or None if not found/expired
        """
        cache_file = self._get_cache_path(key)

        if not cache_file.exists():
            return None

        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Check if expired
            cached_time = datetime.fromisoformat(data['timestamp'])
            if datetime.now() - cached_time > self.ttl:
                logger.debug(f"Cache expired for key: {key}")
                cache_file.unlink()  # Delete expired cache
                return None

            logger.debug(f"Cache hit for key: {key}")
            return data['value']

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            logger.warning(f"Error reading cache: {e}")
            return None

    def set(self, key: str, value: Any) -> None:
        """Set cached value.

        Args:
            key: Cache key
            value: Value to cache (must be JSON serializable)
        """
        cache_file = self._get_cache_path(key)

        data = {
            'timestamp': datetime.now().isoformat(),
            'key': key,
            'value': value
        }

        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            logger.debug(f"Cached value for key: {key}")
        except (TypeError, ValueError) as e:
            logger.error(f"Error caching value: {e}")

    def delete(self, key: str) -> None:
        """Delete cached value.

        Args:
            key: Cache key
        """
        cache_file = self._get_cache_path(key)
        if cache_file.exists():
            cache_file.unlink()
            logger.debug(f"Deleted cache for key: {key}")

    def clear(self) -> int:
        """Clear all cached files.

        Returns:
            Number of files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            cache_file.unlink()
            count += 1

        logger.info(f"Cleared {count} cache files")
        return count

    def clean_expired(self) -> int:
        """Remove expired cache files.

        Returns:
            Number of expired files deleted
        """
        count = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)

                cached_time = datetime.fromisoformat(data['timestamp'])
                if datetime.now() - cached_time > self.ttl:
                    cache_file.unlink()
                    count += 1

            except (json.JSONDecodeError, KeyError, ValueError):
                # Delete corrupted cache files
                cache_file.unlink()
                count += 1

        if count > 0:
            logger.info(f"Cleaned {count} expired cache files")

        return count


def cached(cache_instance: Cache, key_func: Optional[Callable] = None):
    """Decorator to cache function results.

    Args:
        cache_instance: Cache instance to use
        key_func: Function to generate cache key from args

    Example:
        >>> cache = Cache()
        >>> @cached(cache, lambda x: f"paper_{x}")
        ... def expensive_operation(paper_id):
        ...     # Do expensive work
        ...     return result
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Default: use function name and args
                key = f"{func.__name__}_{str(args)}_{str(kwargs)}"

            # Try to get from cache
            result = cache_instance.get(key)
            if result is not None:
                return result

            # Compute and cache
            result = func(*args, **kwargs)
            cache_instance.set(key, result)
            return result

        return wrapper
    return decorator
