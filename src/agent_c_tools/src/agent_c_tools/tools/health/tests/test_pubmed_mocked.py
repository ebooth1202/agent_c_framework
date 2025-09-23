"""
Simple Working Mocked PubMed Tests

Let's start with just ONE working mock test to understand the basics.
We'll build up from there once this works.
"""

import pytest
import json
from unittest.mock import patch, AsyncMock

# Import path setup
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from health_nlim.pubmed import PubMedTools


class TestPubMedSimpleMocked:
    """
    Simple mocked tests - starting with just one working example
    """

    def setup_method(self):
        """Set up each test"""
        self.pubmed = PubMedTools()
        self.pubmed.api_key = "fake_test_key"
        self.pubmed.tool_cache = None

    @pytest.mark.asyncio
    async def test_simple_mock_with_patch_object(self):
        """
        Test 1: Simple mock using patch.object

        Instead of mocking aiohttp, let's mock the PubMed methods directly.
        This is much simpler and avoids async context manager issues.
        """
        # Mock the internal search method to return fake data
        fake_articles = [
            {
                "title": "Fake Diabetes Study",
                "authors": ["Dr. Test", "Prof. Mock"],
                "journal": "Fake Journal",
                "pubDate": "2024",
                "doi": "10.1234/fake",
                "abstract": "Fake abstract",
                "pmid": "12345"
            }
        ]

        # Mock the search_articles method directly
        with patch.object(self.pubmed, 'search_articles', return_value=fake_articles) as mock_search:
            # Call get_articles - it will use our fake data
            result = await self.pubmed.get_articles(query="diabetes", max_results=2)

            # Parse result
            result_data = json.loads(result)

            # Verify it worked
            assert "articles" in result_data
            assert len(result_data["articles"]) == 1
            assert result_data["articles"][0]["title"] == "Fake Diabetes Study"

            # Verify the method was called correctly
            mock_search.assert_called_once_with("diabetes", 2)

            print("✅ Simple mock worked! No network calls made.")
            print(f"   Got fake article: {result_data['articles'][0]['title']}")

    @pytest.mark.asyncio
    async def test_mock_empty_results(self):
        """
        Test 2: Mock empty search results
        """
        # Mock search_articles to return empty list
        with patch.object(self.pubmed, 'search_articles', return_value=[]):
            result = await self.pubmed.get_articles(query="raredisease123")
            result_data = json.loads(result)

            assert "articles" in result_data
            assert len(result_data["articles"]) == 0

            print("✅ Empty results mock worked!")

    @pytest.mark.asyncio
    async def test_mock_exception(self):
        """
        Test 3: Mock an exception being thrown
        """
        # Mock search_articles to raise an exception
        with patch.object(self.pubmed, 'search_articles', side_effect=Exception("Fake network error")):
            result = await self.pubmed.get_articles(query="test")
            result_data = json.loads(result)

            # Should handle the exception gracefully
            assert "error" in result_data
            assert "Failed to search PubMed" in result_data["error"]

            print("✅ Exception mock worked!")


# ==========================================
# WHY THIS SIMPLER APPROACH WORKS
# ==========================================
"""
WHAT WE'RE DOING DIFFERENTLY:

❌ BEFORE (Broken):
- Trying to mock aiohttp.ClientSession
- Complex async context manager mocking
- Fighting with asyncio protocols

✅ NOW (Working): 
- Mock the PubMed object's own methods
- Much simpler - just replace method behavior
- No async context manager complexity

BENEFITS:
- Actually works! 
- Much easier to understand
- Focuses on testing OUR code logic
- Still avoids network calls

This is often called "method-level mocking" vs "transport-level mocking"
"""

# ==========================================
# HOW TO RUN
# ==========================================
"""
Run these working tests:

pytest tests/test_pubmed_mocked.py -v -s

These should all pass and be very fast!
"""