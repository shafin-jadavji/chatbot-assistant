import pytest
import os
import sys
from unittest.mock import patch, MagicMock
import requests

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.geolocation_service import get_location_from_ip


class TestGeolocationService:
    """Test suite for geolocation service"""

    @patch('services.geolocation_service.requests.get')
    def test_get_location_from_ip_success(self, mock_get):
        """Test successful geolocation lookup"""
        # Mock successful response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "city": "San Francisco",
            "region": "California",
            "country": "US",
            "loc": "37.7749,-122.4194"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = get_location_from_ip("8.8.8.8")
        
        # Assertions
        assert result["city"] == "San Francisco"
        assert result["region"] == "California"
        assert result["country"] == "US"
        assert result["loc"] == "37.7749,-122.4194"
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "https://ipinfo.io/8.8.8.8/json" == args[0]
        assert kwargs["timeout"] == 5
        
    @patch('services.geolocation_service.requests.get')
    def test_get_location_from_ip_request_exception(self, mock_get):
        """Test handling of request exceptions"""
        # Mock the request to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")
        
        result = get_location_from_ip("8.8.8.8")
        
        # Assertions
        assert result is None
        
    @patch('services.geolocation_service.requests.get')
    def test_get_location_from_ip_http_error(self, mock_get):
        """Test handling of HTTP errors"""
        # Mock response with HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Not Found")
        mock_get.return_value = mock_response
        
        result = get_location_from_ip("8.8.8.8")
        
        # Assertions
        assert result is None
        
    @patch('services.geolocation_service.requests.get')
    def test_get_location_from_ip_json_error(self, mock_get):
        """Test handling of JSON parsing errors"""
        # Mock successful response but make json() raise an exception
        mock_response = MagicMock()
        mock_response.raise_for_status = MagicMock()
        mock_response.json.side_effect = ValueError("Invalid JSON")
        mock_get.return_value = mock_response
        
        result = get_location_from_ip("8.8.8.8")
        
        # Assertions
        assert result is None
        
    @patch('services.geolocation_service.requests.get')
    def test_get_location_from_ip_missing_data(self, mock_get):
        """Test handling of response with missing data"""
        # Mock response with incomplete data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            # Missing city and other fields
            "ip": "8.8.8.8"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response
        
        result = get_location_from_ip("8.8.8.8")
        
        # Assertions
        assert result["city"] is None
        assert result["region"] is None
        assert result["country"] is None
        assert result["loc"] is None