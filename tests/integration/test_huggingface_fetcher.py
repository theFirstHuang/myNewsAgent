"""Integration tests for HuggingFace fetcher."""

import pytest
import requests


class TestHuggingFaceIntegration:
    """Test HuggingFace integration."""

    def test_huggingface_papers_accessible(self):
        """Test HuggingFace papers page is accessible."""
        url = "https://huggingface.co/papers"

        try:
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Test)'}
            )
            assert response.status_code == 200
            assert len(response.content) > 1000  # Should have substantial content

        except requests.RequestException:
            pytest.skip("HuggingFace not accessible (network issue)")

    def test_huggingface_response_is_html(self):
        """Test HuggingFace returns HTML."""
        url = "https://huggingface.co/papers"

        try:
            response = requests.get(
                url,
                timeout=10,
                headers={'User-Agent': 'Mozilla/5.0 (Test)'}
            )

            content_type = response.headers.get('content-type', '')
            assert 'html' in content_type.lower()

        except requests.RequestException:
            pytest.skip("HuggingFace not accessible")
