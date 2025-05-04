# src/agent_c_api/tests/v2/test_api_structure.py
from fastapi.testclient import TestClient
from agent_c_api.main import app

client = TestClient(app)

def test_v2_api_route_exists():
    """Test that the /api/v2 route exists and returns 404 (since no endpoints are implemented yet)"""
    response = client.get("/api/v2")
    # Should be 404 since we haven't implemented any endpoints at the root yet
    assert response.status_code == 404
    
    # Test that the app is working correctly - the docs should be accessible
    response = client.get("/docs")
    assert response.status_code == 200