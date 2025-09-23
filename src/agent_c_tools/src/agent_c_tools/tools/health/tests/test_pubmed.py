"""
Simple PubMed Tests - Starting Small

This is a beginner-friendly test file with just the basics.
We'll add more tests as we learn.

The sys.path fix below means you can run tests with just:
pytest tests/test_pubmed.py -v -s
(no need for PYTHONPATH=. anymore!)
"""

import pytest
import json
import os
import asyncio

# Try to load .env file from root directory
try:
    from dotenv import load_dotenv

    # Look for .env file in parent directories
    env_path = None
    current_dir = os.path.dirname(os.path.abspath(__file__))
    for i in range(10):  # Check up to 10 levels up (increased for deep project structures)
        potential_env = os.path.join(current_dir, '.env')
        if os.path.exists(potential_env):
            env_path = potential_env
            break
        current_dir = os.path.dirname(current_dir)

    if env_path:
        load_dotenv(env_path)
        print(f"✅ Loaded .env file from: {env_path}")
    else:
        print("❌ No .env file found in parent directories")
except ImportError:
    print("⚠️  python-dotenv not installed - install with: pip install python-dotenv")

# Fix import path so we can import health_nlim from the parent directory
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the PubMed tool we want to test
from health_nlim.pubmed import PubMedTools


class TestPubMedBasics:
    """
    Basic tests for PubMed tool

    These tests will help us understand:
    1. How to make real API calls
    2. How to test for errors
    3. How to check if results look right
    """

    def setup_method(self):
        """
        This runs before each test
        Creates a fresh PubMed tool for each test
        """
        # Create the tool
        self.pubmed = PubMedTools()

        # Make sure we have an API key from .env file
        self.pubmed.api_key = os.getenv('PUBMED_API_KEY')

        # Turn off caching for testing (keeps things simple)
        self.pubmed.tool_cache = None

    # ==========================================
    # TEST 0: Check API Key Setup
    # ==========================================

    def test_api_key_setup(self):
        """
        Test 0: Check if API key is properly loaded

        This helps us debug API key issues before trying real API calls
        """
        # Debug: Show current working directory
        print(f"Current working directory: {os.getcwd()}")

        # Check if .env file exists in current directory
        env_file_exists = os.path.exists('.env')
        print(f".env file exists in current directory: {env_file_exists}")

        # Check if API key is loaded
        api_key = os.getenv('PUBMED_API_KEY')

        print(f"API Key from environment: {api_key[:10]}")
        print(f"PubMed tool API key: {self.pubmed.api_key[:10]}")

        # This test will tell us if the problem is API key loading
        if api_key is None:
            print("❌ No PUBMED_API_KEY found in environment variables")
            print("💡 The .env file might not be loaded or in wrong location")

            # Try to manually read .env file if it exists
            if env_file_exists:
                print("🔍 Found .env file, trying to read it manually...")
                try:
                    with open('.env', 'r') as f:
                        content = f.read()
                        if 'PUBMED_API_KEY' in content:
                            print("✅ PUBMED_API_KEY found in .env file")
                            print("❌ But it's not loaded into environment - need python-dotenv")
                        else:
                            print("❌ PUBMED_API_KEY not found in .env file")
                except Exception as e:
                    print(f"❌ Error reading .env file: {e}")
        else:
            print(f"✅ API key found: {api_key[:10]}...")  # Show first 10 chars only

    # ==========================================
    # TEST 1: Real API Call
    # ==========================================

    @pytest.mark.skipif(os.getenv('PUBMED_API_KEY') is None, reason="No PUBMED_API_KEY found in environment")
    @pytest.mark.asyncio
    async def test_real_api_call(self):
        """
        Test 1: Make a real call to PubMed API

        This test actually hits the real PubMed API to make sure:
        - Our API key works
        - We can get results back
        - The basic flow works
        """
        # Call the PubMed tool with a simple search
        result = await self.pubmed.get_articles(query="diabetes", max_results=2)

        # Convert the JSON string result back to Python object
        result_data = json.loads(result)

        # Check that we got articles back (not an error)
        assert "articles" in result_data
        assert "error" not in result_data

        # Check that we got some results (diabetes should return results)
        articles = result_data["articles"]
        assert len(articles) > 0

        print(f"✅ Got {len(articles)} articles about diabetes")

    # ==========================================
    # TEST 2: Missing Query Parameter
    # ==========================================

    @pytest.mark.asyncio
    async def test_missing_query(self):
        """
        Test 2: What happens when we don't provide a query?

        This tests error handling - the tool should give us
        a helpful error message, not crash.
        """
        # Call without providing a query parameter
        result = await self.pubmed.get_articles()

        # Convert result to Python object
        result_data = json.loads(result)

        # Should get an error, not articles
        assert "error" in result_data
        assert "articles" not in result_data

        # Error message should be helpful
        error_message = result_data["error"]
        assert "required" in error_message.lower()

        print(f"✅ Got expected error: {error_message}")

    # ==========================================
    # TEST 3: Empty Query
    # ==========================================

    @pytest.mark.asyncio
    async def test_empty_query(self):
        """
        Test 3: What happens with empty string query?

        This is another error case - empty string should
        be treated like missing query.
        """
        # Call with empty string
        result = await self.pubmed.get_articles(query="")

        result_data = json.loads(result)

        # Should get an error
        assert "error" in result_data
        assert "required" in result_data["error"].lower()

        print(f"✅ Empty query handled correctly")

    # ==========================================
    # TEST 4: Check Result Format
    # ==========================================

    @pytest.mark.skipif(os.getenv('PUBMED_API_KEY') is None, reason="No PUBMED_API_KEY found in environment")
    @pytest.mark.asyncio
    async def test_result_format(self):
        """
        Test 4: Check that results have the right structure

        When we get articles back, they should have:
        - title
        - authors
        - journal
        - pmid (PubMed ID)
        """
        # Get some results
        result = await self.pubmed.get_articles(query="aspirin", max_results=1)
        result_data = json.loads(result)

        # Should have articles
        assert "articles" in result_data
        articles = result_data["articles"]

        if len(articles) > 0:
            # Check first article has expected fields
            first_article = articles[0]

            # These fields should exist
            assert "title" in first_article
            assert "authors" in first_article
            assert "journal" in first_article
            assert "pmid" in first_article

            # Title should not be empty
            assert len(first_article["title"]) > 0

            print(f"✅ Article format looks good:")
            print(f"   Title: {first_article['title'][:50]}...")
            print(f"   Journal: {first_article['journal']}")
            print(f"   PMID: {first_article['pmid']}")


# ==========================================
# HOW TO RUN THESE TESTS
# ==========================================
"""
1. Make sure you have pytest installed:
   pip install pytest pytest-asyncio

2. From the health/ directory, run:
   pytest tests/test_pubmed.py -v -s

3. To check if your API key is set up:
   pytest tests/test_pubmed.py::TestPubMedBasics::test_api_key_setup -v -s

4. If you want to test real API calls, add PUBMED_API_KEY to your .env file:
   PUBMED_API_KEY=your_actual_api_key_here

   (No more PYTHONPATH needed - the import fix is built into the file!)

The -v shows each test name
The -s shows the print statements

Examples:
- Run all tests: pytest tests/test_pubmed.py -v -s  
- Run one test: pytest tests/test_pubmed.py::TestPubMedBasics::test_missing_query -v -s
- Check API setup: pytest tests/test_pubmed.py::TestPubMedBasics::test_api_key_setup -v -s
"""