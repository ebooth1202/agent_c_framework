"""
conftest.py - Shared pytest configuration for health tools tests

This file contains pytest fixtures and configuration that can be shared
across all test files in the health/tests/ directory.

This tests/ directory is completely self-contained with:
- All test files (test_*.py)
- Test configuration (conftest.py)
- Test dependencies (health_requirements.txt)
- Test package setup (__init__.py)

Pytest automatically discovers and loads conftest.py files, making the
fixtures defined here available to all test files in this directory
and subdirectories.
"""

import pytest
import os
from unittest.mock import Mock


@pytest.fixture
def mock_cache():
    """
    Fixture providing a mock cache for testing

    This can be used by any test that needs a mock cache object.
    Usage in test method:
        def test_something(self, mock_cache):
            # use mock_cache here
    """
    cache = Mock()
    cache.get.return_value = None  # Default to cache miss
    return cache


@pytest.fixture
def sample_env_vars():
    """
    Fixture for setting up environment variables needed for testing

    This sets up fake API keys and other environment variables
    so tests don't need real credentials.
    """
    original_env = {}
    test_env_vars = {
        'PUBMED_API_KEY': 'test_pubmed_key_12345',
        'FDA_API_KEY': 'test_fda_key_67890',
        'CLINICAL_TRIALS_API_KEY': 'test_trials_key_abcde'
    }

    # Store original values
    for key in test_env_vars:
        original_env[key] = os.environ.get(key)
        os.environ[key] = test_env_vars[key]

    yield test_env_vars

    # Restore original values after test
    for key, original_value in original_env.items():
        if original_value is None:
            os.environ.pop(key, None)
        else:
            os.environ[key] = original_value


@pytest.fixture
def sample_pubmed_article():
    """
    Fixture providing sample PubMed article data for testing

    This represents what a typical article response might look like
    """
    return {
        "title": "Sample Medical Research Article",
        "authors": ["Smith, John A", "Jones, Mary B", "Brown, David C"],
        "journal": "Journal of Medical Research",
        "pubDate": "2024 Jan",
        "doi": "10.1234/example.2024.001",
        "abstract": "This is a sample abstract for testing purposes. It describes a hypothetical medical study about treatment effectiveness.",
        "pmid": "12345678"
    }


@pytest.fixture
def sample_clinical_trial():
    """
    Fixture providing sample clinical trial data for testing
    """
    return {
        "nctId": "NCT12345678",
        "title": "Sample Clinical Trial for Testing",
        "status": "Recruiting",
        "phase": ["Phase 2"],
        "conditions": ["Diabetes Mellitus, Type 2"],
        "locations": ["Mayo Clinic, Rochester, MN, United States"],
        "lastUpdated": "2024-01-15"
    }


@pytest.fixture
def sample_fda_drug():
    """
    Fixture providing sample FDA drug data for testing
    """
    return {
        "generic_name": "ibuprofen",
        "brand_name": "Advil",
        "labeler_name": "Pfizer Inc.",
        "product_ndc": "0573-0164",
        "dosage_form": "TABLET",
        "route": "ORAL",
        "marketing_status": "Prescription"
    }


# Pytest configuration options
def pytest_configure(config):
    """
    Global pytest configuration

    This function runs once when pytest starts up.
    You can add custom markers or configuration here.
    """
    # Add custom markers
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests that require API access"
    )


# Optional: Async event loop configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """
    Create an instance of the default event loop for the test session.

    This ensures async tests work properly.
    """
    import asyncio
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


# Example of how to use markers in your tests:
"""
@pytest.mark.slow
async def test_large_dataset(self):
    # This test will be skipped when running: pytest -m "not slow"
    pass

@pytest.mark.integration  
async def test_real_api_call(self):
    # This test hits real APIs - mark as integration test
    pass
"""