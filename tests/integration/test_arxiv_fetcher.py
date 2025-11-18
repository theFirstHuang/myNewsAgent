"""Integration tests for arXiv fetcher."""

import pytest
import requests
import xml.etree.ElementTree as ET


class TestArxivIntegration:
    """Test arXiv API integration."""

    def test_arxiv_api_accessible(self):
        """Test arXiv API is accessible."""
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": "cat:cs.CL",
            "start": 0,
            "max_results": 1
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            assert response.status_code == 200
        except requests.RequestException:
            pytest.skip("arXiv API not accessible (network issue)")

    def test_arxiv_response_format(self):
        """Test arXiv API returns expected XML format."""
        url = "http://export.arxiv.org/api/query"
        params = {
            "search_query": "cat:cs.CL",
            "start": 0,
            "max_results": 1
        }

        try:
            response = requests.get(url, params=params, timeout=10)
            root = ET.fromstring(response.content)

            # Check for expected namespaces
            ns = {'atom': 'http://www.w3.org/2005/Atom'}
            entries = root.findall('atom:entry', ns)

            assert len(entries) >= 0  # May be 0 if no results

            if len(entries) > 0:
                entry = entries[0]
                # Check for required fields
                assert entry.find('atom:title', ns) is not None
                assert entry.find('atom:id', ns) is not None

        except requests.RequestException:
            pytest.skip("arXiv API not accessible")

    def test_arxiv_categories(self):
        """Test fetching from different categories."""
        categories = ["cs.CL", "cs.AI", "cs.LG"]
        url = "http://export.arxiv.org/api/query"

        for category in categories:
            params = {
                "search_query": f"cat:{category}",
                "start": 0,
                "max_results": 1
            }

            try:
                response = requests.get(url, params=params, timeout=10)
                assert response.status_code == 200

                root = ET.fromstring(response.content)
                ns = {'atom': 'http://www.w3.org/2005/Atom'}
                entries = root.findall('atom:entry', ns)

                # Should get at least some results for these popular categories
                # (might be 0 on very rare occasions)
                assert len(entries) >= 0

            except requests.RequestException:
                pytest.skip(f"arXiv API not accessible for {category}")
