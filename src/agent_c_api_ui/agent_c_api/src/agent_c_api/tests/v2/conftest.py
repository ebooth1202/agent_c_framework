# src/agent_c_api/tests/v2/conftest.py
import pytest
from fastapi.testclient import TestClient
from agent_c_api.main import app

@pytest.fixture
def client():
    """Test client fixture for the FastAPI application"""
    return TestClient(app)