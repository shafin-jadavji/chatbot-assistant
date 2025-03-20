import os
import sys

# Add the project root directory to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import modules that depend on the 'backend' package
from transformers import pipeline
import logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Load a pre-trained transformer model for intent classification
try:
    intent_classifier = pipeline("text-classification", model="facebook/bart-large-mnli")
    logger.info("Successfully loaded intent classification model")
except Exception as e:
    logger.error(f"Failed to load intent classification model: {str(e)}")
    raise

# Known intents with expanded keywords
INTENT_LABELS = {
    "weather": ["weather", "temperature", "forecast", "rain", "sunny", "climate", "humidity"],
    "news": ["news", "headlines", "latest", "update", "current events", "breaking", "article", "report"],
    "casual": ["joke", "who are you", "hello", "hi", "how are you", "your name"],
    "stocks": ["stock", "market", "investment", "share", "price", "ticker", "nasdaq", "dow", "s&p"]
}

# News categories for more specific news intent detection
NEWS_CATEGORIES = {
    "business": ["business", "economy", "economic", "finance", "financial", "market", "company", "companies"],
    "technology": ["technology", "tech", "digital", "software", "hardware", "ai", "artificial intelligence", "computer"],
    "health": ["health", "medical", "medicine", "disease", "healthcare", "doctor", "hospital", "covid", "pandemic"],
    "science": ["science", "scientific", "research", "discovery", "space", "physics", "biology", "chemistry"],
    "sports": ["sports", "sport", "game", "match", "tournament", "player", "team", "football", "basketball", "baseball", "soccer"],
    "entertainment": ["entertainment", "movie", "film", "music", "celebrity", "actor", "actress", "hollywood", "tv", "television"]
}

logger.debug(f"Configured intent labels: {INTENT_LABELS}")
logger.debug(f"Configured news categories: {NEWS_CATEGORIES}")

def detect_intent(user_message):
    """
    Uses transformer model to classify user intent.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: Detected intent category
    """
    logger.debug(f"Detecting intent for message: '{user_message}'")
    
    try:
        prediction = intent_classifier(user_message)[0]
        label = prediction["label"].lower()
        score = prediction["score"]
        logger.debug(f"Raw model prediction: {label} (score: {score:.4f})")
        
        # Convert message to lowercase for case-insensitive matching
        message_lower = user_message.lower()
        
        # Special case for stock market indices
        if any(index in message_lower for index in ["nasdaq", "dow", "s&p"]):
            logger.info(f"Detected intent 'stocks' based on market index keywords")
            return "stocks"
        
        # Check for intent keywords in the message
        for intent, keywords in INTENT_LABELS.items():
            for keyword in keywords:
                # For multi-word keywords (phrases)
                if " " in keyword and keyword in message_lower:
                    logger.info(f"Detected intent '{intent}' based on phrase '{keyword}'")
                    return intent
                # For single-word keywords, use simpler contains check
                elif keyword in message_lower.split():
                    logger.info(f"Detected intent '{intent}' based on keyword '{keyword}'")
                    return intent
        
        # If no intent was matched, return "general"
        logger.info("No specific intent detected, defaulting to 'general'")
        return "general"
    
    except Exception as e:
        logger.error(f"Error detecting intent: {str(e)}", exc_info=True)
        logger.warning("Falling back to 'general' intent due to error")
        return "general"  # Default in case of error

def detect_news_category(user_message):
    """
    Detects specific news category from user message
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str or None: Detected news category or None if not found
    """
    message_lower = user_message.lower()
    
    for category, keywords in NEWS_CATEGORIES.items():
        if any(keyword in message_lower for keyword in keywords):
            logger.info(f"Detected news category: {category}")
            return category
            
    logger.info("No specific news category detected")
    return None

def extract_news_query(user_message):
    """
    Extracts potential search query from news request
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str or None: Extracted query or None
    """
    # Simple extraction based on common patterns
    message_lower = user_message.lower()
    
    query_indicators = [
        "about", "on", "regarding", "related to", "search for", 
        "find", "look up", "tell me about"
    ]
    
    for indicator in query_indicators:
        if indicator in message_lower:
            # Extract text after the indicator
            parts = message_lower.split(indicator, 1)
            if len(parts) > 1 and parts[1].strip():
                query = parts[1].strip()
                logger.info(f"Extracted news query: '{query}'")
                return query
                
    logger.info("No specific news query detected")
    return None

def detect_temperature_unit(user_message):
    """
    Detects if the user has specified a temperature unit preference.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: "metric" for Celsius, "imperial" for Fahrenheit, or None if not specified
    """
    message_lower = user_message.lower()
    
    # Check for Celsius indicators
    celsius_indicators = ["celsius", "centigrade", "°c", " c ", "degrees c"]
    if any(indicator in message_lower for indicator in celsius_indicators):
        logger.info("Detected temperature unit preference: Celsius")
        return "metric"
        
    # Check for Fahrenheit indicators
    fahrenheit_indicators = ["fahrenheit", "°f", " f ", "degrees f"]
    if any(indicator in message_lower for indicator in fahrenheit_indicators):
        logger.info("Detected temperature unit preference: Fahrenheit")
        return "imperial"
        
    # Default case - no specific unit mentioned
    logger.debug("No specific temperature unit detected in message")
    return None

# --- TEST FUNCTION ---
def test_intent_detection():
    logger.info("Starting intent detection test")
    test_messages = [
        "What's the weather in Phoenix?",  # Should detect as "weather"
        "Whats the temperature?",  # Should detect as "weather"
        "Tell me the latest news!",  # Should detect as "news"
        "What's happening in technology news?",  # Should detect as "news" with category "technology"
        "Show me news about climate change",  # Should detect as "news" with query "climate change"
        "Who are you?",  # Should detect as "casual"
        "I love programming!",  # Should detect as "general"
        "What's the stock price of Apple?",  # Should detect as "stocks"
        "Tell me about business news",  # Should detect as "news" with category "business"
    ]

    for i, message in enumerate(test_messages):
        logger.info(f"Test {i+1}/{len(test_messages)}: Processing '{message}'")
        intent = detect_intent(message)
        logger.info(f"Message: '{message}' -> Intent: '{intent}'")
        
        if intent == "news":
            category = detect_news_category(message)
            query = extract_news_query(message)
            logger.info(f"  News category: {category}, Query: {query}")
    
    logger.info("Intent detection test completed")

if __name__ == "__main__":
    from utils.logging_config import setup_logging
    setup_logging(logging.DEBUG)
    test_intent_detection()