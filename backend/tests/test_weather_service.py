import pytest
import os
import sys
from unittest.mock import patch, MagicMock
import requests
from datetime import datetime, timedelta

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.weather_service import get_weather
from utils.logging_config import get_logger

# Get logger for this test module
logger = get_logger(__name__)

class TestWeatherService:
    """Test suite for weather service functions"""

    @patch('services.weather_service.requests.get')
    def test_get_weather_success(self, mock_get):
        """Test successful API call to get weather data"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "weather": [{"description": "clear sky"}],
            "main": {
                "temp": 72.5,
                "feels_like": 70.2,
                "humidity": 65
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = get_weather("New York", "imperial")

        # Assertions
        assert "New York" in result
        assert "clear sky" in result
        assert "72.5°F" in result
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "api.openweathermap.org/data/2.5/weather" in args[0]
        assert "New York" in args[0]
        assert "imperial" in args[0]
        assert kwargs["timeout"] == 5

    @patch('services.weather_service.requests.get')
    def test_get_weather_metric_units(self, mock_get):
        """Test weather API call with metric units"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "weather": [{"description": "cloudy"}],
            "main": {
                "temp": 22.5,
                "feels_like": 21.0,
                "humidity": 70
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = get_weather("London", "metric")

        # Assertions
        assert "London" in result
        assert "cloudy" in result
        assert "22.5°C" in result

        # Verify the API was called with correct parameters
        args, kwargs = mock_get.call_args
        assert "metric" in args[0]

    @patch('services.weather_service.requests.get')
    def test_get_weather_default_unit(self, mock_get):
        """Test weather API call with default unit (imperial)"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "weather": [{"description": "rainy"}],
            "main": {
                "temp": 65.3,
                "feels_like": 63.0,
                "humidity": 80
            }
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function without specifying unit
        result = get_weather("Tokyo")

        # Assertions
        assert "Tokyo" in result
        assert "rainy" in result
        assert "65.3°F" in result

        # Verify the API was called with imperial units by default
        args, kwargs = mock_get.call_args
        assert "imperial" in args[0]

    @patch('services.weather_service.requests.get')
    def test_get_weather_city_not_found(self, mock_get):
        """Test handling of city not found error"""
        # Mock the API response for a 404 error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("404 Client Error")
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call the function
        result = get_weather("NonExistentCity")

        # Assertions
        assert "Could not find weather data" in result
        assert "NonExistentCity" in result
        assert "check the city name" in result

    @patch('services.weather_service.requests.get')
    def test_get_weather_http_error(self, mock_get):
        """Test handling of HTTP errors"""
        # Mock the API response for a generic HTTP error
        mock_response = MagicMock()
        mock_response.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")
        mock_response.status_code = 500
        mock_get.return_value = mock_response

        # Call the function
        result = get_weather("New York")

        # Assertions
        assert "HTTP Error" in result

    @patch('services.weather_service.requests.get')
    def test_get_weather_request_exception(self, mock_get):
        """Test handling of request exceptions"""
        # Mock the request to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        # Call the function
        result = get_weather("New York")

        # Assertions
        assert "issue connecting to the weather service" in result
        assert "Try again later" in result

    @patch('services.weather_service.requests.get')
    def test_get_weather_incomplete_data(self, mock_get):
        """Test handling of incomplete weather data"""
        # Mock the API response with incomplete data
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "cod": 200,  # Success code but missing required data
            "name": "New York"
            # Missing 'weather' and 'main' fields
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function
        result = get_weather("New York")

        # Assertions
        assert "Weather data is unavailable" in result

    @patch('services.weather_service.WEATHER_API_KEY', None)
    def test_get_weather_missing_api_key(self):
        """Test handling of missing API key"""
        # Call the function when API key is missing
        result = get_weather("New York")

        # Assertions
        assert "Weather API key is missing" in result
        assert "Please configure it" in result

    @patch('services.weather_service.requests.get')
    def test_get_weather_with_time_period(self, mock_get):
        """Test weather API call with time period parameter"""
        # Mock the API response for forecast
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "list": [
                {
                    "dt": int((datetime.now() + timedelta(days=1)).timestamp()),
                    "main": {"temp": 72.5},
                    "weather": [{"main": "Clear", "description": "clear sky"}]
                },
                {
                    "dt": int((datetime.now() + timedelta(days=1, hours=6)).timestamp()),
                    "main": {"temp": 75.2},
                    "weather": [{"main": "Clear", "description": "clear sky"}]
                }
            ],
            "city": {"name": "New York"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function with tomorrow as time period
        result = get_weather("New York", "imperial", "tomorrow")

        # Assertions
        assert "New York" in result
        assert "Tomorrow" in result or "tomorrow" in result
        assert "forecast" in result.lower()
        
        # Verify the API was called with correct parameters
        args, kwargs = mock_get.call_args
        assert "api.openweathermap.org/data/2.5/forecast" in args[0]
        assert "New York" in args[0]
        assert "imperial" in args[0]

    @patch('services.weather_service.requests.get')
    def test_get_weather_with_week_time_period(self, mock_get):
        """Test weather API call with week time period"""
        # Mock the API response for 5-day forecast
        mock_response = MagicMock()
        
        # Create forecast data for 5 days
        forecast_list = []
        for i in range(5):
            forecast_list.append({
                "dt": int((datetime.now() + timedelta(days=i)).timestamp()),
                "main": {"temp": 70 + i},
                "weather": [{"main": "Clear", "description": "clear sky"}]
            })
        
        mock_response.json.return_value = {
            "list": forecast_list,
            "city": {"name": "Seattle"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function with week as time period
        result = get_weather("Seattle", "imperial", "week")

        # Assertions
        assert "Seattle" in result
        assert "5-day forecast" in result
        assert "Monday" in result or "Tuesday" in result or "Wednesday" in result  # At least one day name
        
        # Verify the API was called with correct parameters
        args, kwargs = mock_get.call_args
        assert "api.openweathermap.org/data/2.5/forecast" in args[0]
        assert "Seattle" in args[0]

    @patch('services.weather_service.requests.get')
    def test_get_weather_with_specific_day(self, mock_get):
        """Test weather API call with specific day of week"""
        # Mock the API response for specific day forecast
        mock_response = MagicMock()
        
        # Get the target day (next Monday)
        today = datetime.now()
        days_until_monday = (7 - today.weekday()) % 7
        if days_until_monday == 0:
            days_until_monday = 7  # Next Monday, not today
        target_day = today + timedelta(days=days_until_monday)
        
        # Create forecast data for that day
        forecast_list = []
        for hour in [9, 12, 18]:  # Morning, afternoon, evening
            forecast_list.append({
                "dt": int((target_day.replace(hour=hour)).timestamp()),
                "main": {"temp": 60 + hour//3},
                "weather": [{"main": "Clouds" if hour < 12 else "Clear", "description": "cloudy" if hour < 12 else "clear sky"}]
            })
        
        mock_response.json.return_value = {
            "list": forecast_list,
            "city": {"name": "Chicago"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function with monday as time period
        result = get_weather("Chicago", "imperial", "monday")

        # Assertions
        assert "Chicago" in result
        assert "Monday" in result or "monday" in result
        assert "Morning" in result or "Afternoon" in result or "Evening" in result
        
        # Verify the API was called with correct parameters
        args, kwargs = mock_get.call_args
        assert "api.openweathermap.org/data/2.5/forecast" in args[0]
        assert "Chicago" in args[0]

    @patch('services.weather_service.requests.get')
    def test_parse_forecast_data_with_different_time_periods(self, mock_get):
        """Test the parse_forecast_data function with different time periods"""
        from services.weather_service import parse_forecast_data
        
        # Create test forecast data
        now = datetime.now()
        forecast_list = []
        
        # Add data for today
        for hour in [9, 15, 21]:
            forecast_list.append({
                "dt": int(now.replace(hour=hour).timestamp()),
                "main": {"temp": 60 + hour//3},
                "weather": [{"main": "Clear", "description": "clear sky"}]
            })
        
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "list": forecast_list,
            "city": {"name": "Chicago"}
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the function with today as time period
        result = get_weather("Chicago", "imperial", "today")

        # Assertions
        assert "Chicago" in result
        assert "Today" in result or "today" in result
        assert "Morning" in result or "Afternoon" in result or "Evening" in result
        
        # Verify the API was called with correct parameters
        args, kwargs = mock_get.call_args
        assert "api.openweathermap.org/data/2.5/forecast" in args[0]
        assert "Chicago" in args[0]
