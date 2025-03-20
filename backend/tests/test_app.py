import os
import pytest
from fastapi.testclient import TestClient
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to path so we can import the app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# We need to mock the logging setup before importing app
with patch('utils.logging_config.setup_logging'):
    from app import app

client = TestClient(app)

def test_home_endpoint():
    """Test that the root endpoint returns the expected message."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Chatbot API is running with LangChain Agents!"}

def test_cors_middleware_configuration():
    """Test that CORS middleware is properly configured."""
    # Test preflight request
    response = client.options(
        "/",
        headers={
            "Origin": "http://localhost:5173",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "Content-Type",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://localhost:5173"

@patch.dict(os.environ, {"ALLOWED_ORIGINS": "http://test.com,http://example.com"})
def test_custom_allowed_origins():
    """Test that custom allowed origins from environment variables are used."""
    # We need to reimport the app with the patched environment variable
    with patch('utils.logging_config.setup_logging'):
        # Clear module cache to force reimport with new env vars
        if 'app' in sys.modules:
            del sys.modules['app']
        from app import app
        test_client = TestClient(app)
    
    response = test_client.options(
        "/",
        headers={
            "Origin": "http://test.com",
            "Access-Control-Request-Method": "GET",
        },
    )
    assert response.status_code == 200
    assert "access-control-allow-origin" in response.headers
    assert response.headers["access-control-allow-origin"] == "http://test.com"

def test_router_registration():
    """Test that the chat router is registered."""
    # Instead of mocking the router, we'll check if the app has routes from the chat router
    # by looking for a specific route pattern that should be included
    
    # First, clear the module cache to ensure a fresh import
    if 'app' in sys.modules:
        del sys.modules['app']
    
    # Import the app without mocking the router
    with patch('utils.logging_config.setup_logging'):
        from app import app
        
    # Check if any route in the app matches the expected chat route pattern
    # Based on your codebase structure, the chat router likely has a route like '/chat'
    chat_routes = [route for route in app.routes if '/chat' in str(route.path)]
    
    # Assert that at least one chat route exists
    assert len(chat_routes) > 0, "No chat routes found in the application"