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

# Known intents
INTENT_LABELS = {
    "weather": ["weather", "temperature", "forecast"],
    "news": ["news", "update"],
    "casual": ["joke", "who are you"]
}

logger.debug(f"Configured intent labels: {INTENT_LABELS}")

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
        
        # Match detected label to predefined intents
        for key, keywords in INTENT_LABELS.items():
            if any(word in user_message.lower() for word in keywords):
                logger.info(f"Detected intent '{key}' based on keywords in message")
                return key
                
        logger.info(f"No specific intent detected, defaulting to 'general'")
        return "general"  # Default category
    
    except Exception as e:
        logger.error(f"Error detecting intent: {str(e)}", exc_info=True)
        logger.warning("Falling back to 'general' intent due to error")
        return "general"  # Default in case of error

# --- TEST FUNCTION ---
def test_intent_detection():
    logger.info("Starting intent detection test")
    test_messages = [
        "What's the weather in Phoenix?",  # Should detect as "weather"
        "Whats the temperature?",  # Should detect as "weather"
        "Tell me the latest news!",  # Should detect as "news"
        "Who are you?",  # Should detect as "casual"
        "I love programming!"  # Should detect as "general"
    ]

    for i, message in enumerate(test_messages):
        logger.info(f"Test {i+1}/{len(test_messages)}: Processing '{message}'")
        intent = detect_intent(message)
        logger.info(f"Message: '{message}' -> Intent: '{intent}'")
    
    logger.info("Intent detection test completed")

if __name__ == "__main__":
  
    from utils.logging_config import setup_logging
    setup_logging(logging.DEBUG)
    test_intent_detection()