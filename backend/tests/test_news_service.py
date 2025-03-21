import pytest
import json
from unittest.mock import patch, MagicMock
import os
import sys
import requests  # Add this import

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.news_service import NewsService, get_news


class TestNewsService:
    """Test suite for NewsService class"""

    @patch('services.news_service.requests.get')
    def test_get_top_headlines_success(self, mock_get):
        """Test successful API call to get top headlines"""
        # Mock the API response
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "ok",
            "totalResults": 2,
            "articles": [
                {
                    "source": {"id": "test-source", "name": "Test Source"},
                    "title": "Test Article 1",
                    "url": "https://example.com/article1"
                },
                {
                    "source": {"id": "test-source2", "name": "Test Source 2"},
                    "title": "Test Article 2",
                    "url": "https://example.com/article2"
                }
            ]
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        result = NewsService.get_top_headlines(country="us", category="technology")

        # Assertions
        assert result["status"] == "ok"
        assert len(result["articles"]) == 2
        assert result["articles"][0]["title"] == "Test Article 1"
        
        # Verify the API was called with correct parameters
        mock_get.assert_called_once()
        args, kwargs = mock_get.call_args
        assert "https://newsapi.org/v2/top-headlines" == args[0]
        assert kwargs["params"]["country"] == "us"
        assert kwargs["params"]["category"] == "technology"

    @patch('services.news_service.requests.get')
    def test_get_top_headlines_api_error(self, mock_get):
        """Test API error handling"""
        # Mock the API response for an error
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "status": "error",
            "message": "API key invalid"
        }
        mock_response.raise_for_status = MagicMock()
        mock_get.return_value = mock_response

        # Call the method
        result = NewsService.get_top_headlines()

        # Assertions
        assert "error" in result
        assert result["error"] == "API key invalid"

    @patch('services.news_service.requests.get')
    def test_get_top_headlines_request_exception(self, mock_get):
        """Test handling of request exceptions"""
        # Mock the request to raise an exception
        mock_get.side_effect = requests.exceptions.RequestException("Connection error")

        # Call the method
        result = NewsService.get_top_headlines()

        # Assertions
        assert "error" in result
        assert "Connection error" in result["error"]

    def test_format_news_response_with_articles(self):
        """Test formatting news response with articles"""
        # Test data
        news_data = {
            "status": "ok",
            "articles": [
                {
                    "title": "Test Article 1",
                    "source": {"name": "Test Source"},
                    "url": "https://example.com/article1"
                },
                {
                    "title": "Test Article 2",
                    "source": {"name": "Test Source 2"},
                    "url": "https://example.com/article2"
                }
            ]
        }

        # Call the method
        result = NewsService.format_news_response(news_data)

        # Assertions
        assert "Here are the latest headlines:" in result
        assert "Test Article 1 (Test Source)" in result
        assert "https://example.com/article1" in result
        assert "Test Article 2 (Test Source 2)" in result

    def test_format_news_response_with_error(self):
        """Test formatting news response with error"""
        # Test data with error
        news_data = {"error": "API key invalid"}

        # Call the method
        result = NewsService.format_news_response(news_data)

        # Assertions
        assert "Sorry, I couldn't fetch the news" in result
        assert "API key invalid" in result

    def test_format_news_response_no_articles(self):
        """Test formatting news response with no articles"""
        # Test data with no articles
        news_data = {"status": "ok", "articles": []}

        # Call the method
        result = NewsService.format_news_response(news_data)

        # Assertions
        assert "I couldn't find any news articles" in result


class TestGetNews:
    """Test suite for get_news function"""

    @patch('services.news_service.NewsService.get_top_headlines')
    @patch('services.news_service.NewsService.format_news_response')
    def test_get_news_default(self, mock_format, mock_get_headlines):
        """Test get_news with default parameters"""
        # Mock the service methods
        mock_news_data = {"status": "ok", "articles": [{"title": "Test"}]}
        mock_get_headlines.return_value = mock_news_data
        mock_format.return_value = "Formatted news"

        # Call the function
        result = get_news()

        # Assertions
        mock_get_headlines.assert_called_once_with(category=None, query=None)
        mock_format.assert_called_once_with(mock_news_data)
        assert result == "Formatted news"

    @patch('services.news_service.NewsService.get_top_headlines')
    @patch('services.news_service.NewsService.format_news_response')
    def test_get_news_with_category(self, mock_format, mock_get_headlines):
        """Test get_news with category parameter"""
        # Mock the service methods
        mock_news_data = {"status": "ok", "articles": [{"title": "Tech News"}]}
        mock_get_headlines.return_value = mock_news_data
        mock_format.return_value = "Tech news formatted"

        # Call the function
        result = get_news(category="technology")

        # Assertions
        mock_get_headlines.assert_called_once_with(category="technology", query=None)
        mock_format.assert_called_once_with(mock_news_data)
        assert result == "Tech news formatted"

    @patch('services.news_service.NewsService.get_top_headlines')
    @patch('services.news_service.NewsService.format_news_response')
    def test_get_news_with_query(self, mock_format, mock_get_headlines):
        """Test get_news with query parameter"""
        # Mock the service methods
        mock_news_data = {"status": "ok", "articles": [{"title": "Climate News"}]}
        mock_get_headlines.return_value = mock_news_data
        mock_format.return_value = "Climate news formatted"

        # Call the function
        result = get_news(query="climate")

        # Assertions
        mock_get_headlines.assert_called_once_with(category=None, query="climate")
        mock_format.assert_called_once_with(mock_news_data)
        assert result == "Climate news formatted"
