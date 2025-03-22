import pytest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the parent directory to the path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.langchain_service import (
    chat_with_memory, 
    handle_weather_request, 
    handle_news_request, 
    handle_stocks_request,
    conversation_history
)
from langchain.schema import HumanMessage, AIMessage


class TestLangchainService:
    """Test suite for langchain_service.py"""
    
    def setup_method(self):
        """Setup method to clear conversation history before each test"""
        # Clear conversation history
        conversation_history.clear()
    
    @patch('services.langchain_service.detect_intent')
    @patch('services.langchain_service.extract_entities')
    @patch('services.langchain_service.handle_weather_request')
    def test_chat_with_memory_weather_intent(self, mock_weather_handler, mock_extract_entities, mock_detect_intent):
        """Test chat_with_memory with weather intent"""
        # Setup mocks
        mock_detect_intent.return_value = "weather"
        mock_extract_entities.return_value = {"GPE": ["New York"]}
        mock_weather_handler.return_value = "Weather in New York is sunny."
        
        # Call the function
        result = chat_with_memory("What's the weather in New York?")
        
        # Assertions
        mock_detect_intent.assert_called_once_with("What's the weather in New York?")
        mock_extract_entities.assert_called_once_with("What's the weather in New York?", intent="weather")
        mock_weather_handler.assert_called_once_with({"GPE": ["New York"]}, "What's the weather in New York?")
        assert result == "Weather in New York is sunny."
        # Verify conversation history wasn't modified for intent-based routing
        assert len(conversation_history) == 0
    
    @patch('services.langchain_service.detect_intent')
    @patch('services.langchain_service.handle_news_request')
    def test_chat_with_memory_news_intent(self, mock_news_handler, mock_detect_intent):
        """Test chat_with_memory with news intent"""
        # Setup mocks
        mock_detect_intent.return_value = "news"
        mock_news_handler.return_value = "Here are the latest headlines..."
        
        # Call the function
        result = chat_with_memory("Show me the latest news")
        
        # Assertions
        mock_detect_intent.assert_called_once_with("Show me the latest news")
        mock_news_handler.assert_called_once_with("Show me the latest news")
        assert result == "Here are the latest headlines..."
        # Verify conversation history wasn't modified for intent-based routing
        assert len(conversation_history) == 0
    
    @patch('services.langchain_service.detect_intent')
    @patch('services.langchain_service.extract_entities')
    @patch('services.langchain_service.handle_stocks_request')
    def test_chat_with_memory_stocks_intent(self, mock_stocks_handler, mock_extract_entities, mock_detect_intent):
        """Test chat_with_memory with stocks intent"""
        # Setup mocks
        mock_detect_intent.return_value = "stocks"
        mock_extract_entities.return_value = {"ORG": ["Apple"]}
        mock_stocks_handler.return_value = "I'll be able to provide stock information in a future update."
        
        # Call the function
        result = chat_with_memory("How are Apple stocks doing?")
        
        # Assertions
        mock_detect_intent.assert_called_once_with("How are Apple stocks doing?")
        mock_extract_entities.assert_called_once_with("How are Apple stocks doing?", intent="stocks")
        mock_stocks_handler.assert_called_once_with({"ORG": ["Apple"]})
        assert result == "I'll be able to provide stock information in a future update."
        # Verify conversation history wasn't modified for intent-based routing
        assert len(conversation_history) == 0
    
    @patch('services.langchain_service.detect_intent')
    @patch('services.langchain_service.extract_entities')
    @patch('services.langchain_service.llm')
    def test_chat_with_memory_general_conversation(self, mock_llm, mock_extract_entities, mock_detect_intent):
        """Test chat_with_memory with general conversation (no specific intent)"""
        # Setup mocks
        mock_detect_intent.return_value = "general"
        mock_extract_entities.return_value = {}
        
        # Mock the LLM response
        mock_response = MagicMock()
        mock_response.content = "I'm an AI assistant. How can I help you today?"
        mock_llm.invoke.return_value = mock_response
        
        # Call the function
        result = chat_with_memory("Hello, who are you?")
        
        # Assertions
        mock_detect_intent.assert_called_once_with("Hello, who are you?")
        mock_extract_entities.assert_called_once_with("Hello, who are you?", intent="general")
        mock_llm.invoke.assert_called_once()
        
        # Check conversation history was updated
        assert len(conversation_history) == 2
        assert isinstance(conversation_history[0], HumanMessage)
        assert conversation_history[0].content == "Hello, who are you?"
        assert isinstance(conversation_history[1], AIMessage)
        assert conversation_history[1].content == "I'm an AI assistant. How can I help you today?"
        
        assert result == "I'm an AI assistant. How can I help you today?"
    
    @patch('services.langchain_service.get_weather')
    def test_handle_weather_request_with_location(self, mock_get_weather):
        """Test handle_weather_request with a valid location"""
        # Setup mock
        mock_get_weather.return_value = "It's 72°F and sunny in New York."
        
        # Test data
        entities = {"GPE": ["New York"]}
        user_message = "What's the weather in New York?"
        
        # Call the function
        result = handle_weather_request(entities, user_message)
        
        # Assertions
        mock_get_weather.assert_called_once_with("New York", "imperial")
        assert result == "It's 72°F and sunny in New York."
    
    @patch('services.langchain_service.detect_temperature_unit')
    @patch('services.langchain_service.get_weather')
    def test_handle_weather_request_with_celsius_unit(self, mock_get_weather, mock_detect_temp_unit):
        """Test handle_weather_request with Celsius temperature unit"""
        # Setup mocks
        mock_detect_temp_unit.return_value = "metric"
        mock_get_weather.return_value = "It's 22°C and sunny in London."
        
        # Test data
        entities = {"GPE": ["London"]}
        user_message = "What's the weather in London in Celsius?"
        
        # Call the function
        result = handle_weather_request(entities, user_message)
        
        # Assertions
        mock_detect_temp_unit.assert_called_once_with(user_message)
        mock_get_weather.assert_called_once_with("London", "metric")
        assert result == "It's 22°C and sunny in London."
    
    def test_handle_weather_request_without_location(self):
        """Test handle_weather_request without a location"""
        # Test data
        entities = {}
        user_message = "What's the weather like?"
        
        # Call the function
        result = handle_weather_request(entities, user_message)
        
        # Assertions
        assert result == "I need a location to fetch weather details."
    
    @patch('services.langchain_service.detect_news_category')
    @patch('services.langchain_service.extract_news_query')
    @patch('services.langchain_service.get_news')
    def test_handle_news_request(self, mock_get_news, mock_extract_query, mock_detect_category):
        """Test handle_news_request"""
        # Setup mocks
        mock_detect_category.return_value = "technology"
        mock_extract_query.return_value = "AI"
        mock_get_news.return_value = "Here are the latest AI technology headlines..."
        
        # Call the function
        result = handle_news_request("Show me the latest AI technology news")
        
        # Assertions
        mock_detect_category.assert_called_once_with("Show me the latest AI technology news")
        mock_extract_query.assert_called_once_with("Show me the latest AI technology news")
        mock_get_news.assert_called_once_with(category="technology", query="AI")
        assert result == "Here are the latest AI technology headlines..."
    
    def test_handle_stocks_request(self):
        """Test handle_stocks_request"""
        # Test data
        entities = {"ORG": ["Apple"]}
        
        # Call the function
        result = handle_stocks_request(entities)
        
        # Assertions
        assert result == "I'll be able to provide stock information in a future update."
