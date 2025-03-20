import unittest
from unittest.mock import patch, MagicMock
import sys
import os
import logging

# Add the parent directory to sys.path to import modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.intent_service import (
    detect_intent,
    detect_news_category,
    extract_news_query,
    detect_temperature_unit,
    INTENT_LABELS,
    NEWS_CATEGORIES
)

class TestIntentService(unittest.TestCase):
    
    @patch('services.intent_service.intent_classifier')
    def test_detect_intent_weather(self, mock_classifier):
        # Mock the classifier response
        mock_classifier.return_value = [{"label": "LABEL_0", "score": 0.95}]
        
        # Test weather intent detection
        result = detect_intent("What's the weather like in New York?")
        self.assertEqual(result, "weather")
        
        result = detect_intent("Will it rain tomorrow?")
        self.assertEqual(result, "weather")
        
        result = detect_intent("Temperature forecast for the weekend")
        self.assertEqual(result, "weather")
    
    @patch('services.intent_service.intent_classifier')
    def test_detect_intent_news(self, mock_classifier):
        # Mock the classifier response
        mock_classifier.return_value = [{"label": "LABEL_0", "score": 0.95}]
        
        # Test news intent detection
        result = detect_intent("What's the latest news?")
        self.assertEqual(result, "news")
        
        result = detect_intent("Show me today's headlines")
        self.assertEqual(result, "news")
        
        result = detect_intent("Any breaking news?")
        self.assertEqual(result, "news")
    
    @patch('services.intent_service.intent_classifier')
    def test_detect_intent_casual(self, mock_classifier):
        # Mock the classifier response
        mock_classifier.return_value = [{"label": "LABEL_0", "score": 0.95}]
        
        # Test casual intent detection
        result = detect_intent("Hello there")
        self.assertEqual(result, "casual")
        
        result = detect_intent("Who are you?")
        self.assertEqual(result, "casual")
        
        result = detect_intent("Tell me a joke")
        self.assertEqual(result, "casual")
    
    @patch('services.intent_service.intent_classifier')
    def test_detect_intent_stocks(self, mock_classifier):
        # Mock the classifier response
        mock_classifier.return_value = [{"label": "LABEL_0", "score": 0.95}]
        
        # Test stocks intent detection
        result = detect_intent("What's the stock price of Apple?")
        self.assertEqual(result, "stocks")
        
        result = detect_intent("How is the market doing today?")
        self.assertEqual(result, "stocks")
        
        result = detect_intent("Show me NASDAQ updates")
        self.assertEqual(result, "stocks")
    
    @patch('services.intent_service.intent_classifier')
    def test_detect_intent_general(self, mock_classifier):
        # Mock the classifier response
        mock_classifier.return_value = [{"label": "LABEL_0", "score": 0.95}]
        
        # Test general intent (fallback)
        result = detect_intent("Something completely random")
        self.assertEqual(result, "general")
    
    @patch('services.intent_service.intent_classifier')
    def test_detect_intent_error_handling(self, mock_classifier):
        # Mock the classifier to raise an exception
        mock_classifier.side_effect = Exception("Test error")
        
        # Test error handling
        result = detect_intent("This should trigger an error")
        self.assertEqual(result, "general")  # Should default to general on error
    
    def test_detect_news_category(self):
        # Test business category
        result = detect_news_category("Tell me about business news")
        self.assertEqual(result, "business")
        
        # Test technology category
        result = detect_news_category("What's happening in tech?")
        self.assertEqual(result, "technology")
        
        # Test health category
        result = detect_news_category("Latest health updates")
        self.assertEqual(result, "health")
        
        # Test science category
        result = detect_news_category("Any new scientific discoveries?")
        self.assertEqual(result, "science")
        
        # Test sports category
        result = detect_news_category("Show me sports news")
        self.assertEqual(result, "sports")
        
        # Test entertainment category
        result = detect_news_category("Hollywood news today")
        self.assertEqual(result, "entertainment")
        
        # Test no specific category
        result = detect_news_category("Just show me some news")
        self.assertIsNone(result)
    
    def test_extract_news_query(self):
        # Test various query extraction patterns
        result = extract_news_query("Tell me about climate change")
        self.assertEqual(result, "climate change")
        
        result = extract_news_query("Find news regarding artificial intelligence")
        self.assertEqual(result, "artificial intelligence")
        
        result = extract_news_query("Search for COVID updates")
        self.assertEqual(result, "covid updates")
        
        # Test no query extraction
        result = extract_news_query("Just show me the news")
        self.assertIsNone(result)
    
    def test_detect_temperature_unit(self):
        # Test Celsius detection
        result = detect_temperature_unit("What's the temperature in Celsius?")
        self.assertEqual(result, "metric")
        
        result = detect_temperature_unit("Show me the weather in °C")
        self.assertEqual(result, "metric")
        
        # Test Fahrenheit detection
        result = detect_temperature_unit("What's the temperature in Fahrenheit?")
        self.assertEqual(result, "imperial")
        
        result = detect_temperature_unit("Show me the weather in °F")
        self.assertEqual(result, "imperial")
        
        # Test no unit specified
        result = detect_temperature_unit("What's the temperature?")
        self.assertIsNone(result)
    
    def test_intent_labels_coverage(self):
        # Verify all intent labels have keywords
        for intent, keywords in INTENT_LABELS.items():
            self.assertTrue(len(keywords) > 0, f"Intent {intent} has no keywords")
    
    def test_news_categories_coverage(self):
        # Verify all news categories have keywords
        for category, keywords in NEWS_CATEGORIES.items():
            self.assertTrue(len(keywords) > 0, f"News category {category} has no keywords")


if __name__ == "__main__":
    unittest.main()
