import os
import sys

# Add the project root directory to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now import modules that depend on the 'backend' package
import spacy
import logging
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

# Load spaCy model
try:
    nlp = spacy.load("en_core_web_sm")
    logger.info("Successfully loaded spaCy model 'en_core_web_sm'")
except Exception as e:
    logger.error(f"Failed to load spaCy model: {str(e)}")
    raise

def extract_entities(user_message):
    """
    Extracts various entities from user messages using spaCy.
    Returns a dictionary where the values are lists of entities.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        dict: A dictionary of extracted entities
    """
    logger.debug(f"Processing message: '{user_message}'")
    
    doc = nlp(user_message)
    
    entities = {
        "GPE": [],  # Location (City, Country, etc.)
        "PERSON": [],  # Names (e.g., John, Barack Obama)
        "TIME": [],  # Time expressions (e.g., "tomorrow", "3 PM")
        "DATE": [],  # Dates (e.g., "Monday", "March 5")
        "ORG": [],  # Organizations (e.g., Google, NASA)
    }

    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)  # Store all occurrences
            logger.debug(f"Found entity: {ent.text} ({ent.label_})")
    
    logger.info(f"Extracted {sum(len(v) for v in entities.values())} entities from message")
    logger.debug(f"Extracted entities: {entities}")
    
    return entities

# --- TEST FUNCTION ---
def test_entity_extraction():
    logger.info("Starting entity extraction test")
    test_messages = [
        "What's the weather in Phoenix?",  # {"GPE": "Phoenix"}
        "Barack Obama was the 44th President of the United States.",  # {"PERSON": "Barack Obama"}
        "I have a meeting on Monday at 3 PM.",  # {"DATE": "Monday", "TIME": "3 PM"}
        "Google is one of the biggest tech companies.",  # {"ORG": "Google"}
        "What is the temperature in London?",  # {"GPE": "London"}

        "Is Phoenix a city in Arizona?"  # {"GPE": ["Phoenix", "Arizona"]}
    ]


    for i, message in enumerate(test_messages):
        logger.info(f"Test {i+1}/{len(test_messages)}: Processing '{message}'")
        entities = extract_entities(message)

        # Replace print with logging
        logger.info(f"Message: {message} -> Entities: {entities}")
    
    logger.info("Entity extraction test completed")

if __name__ == "__main__":
    # Import and setup logging when running this file directly
    from utils.logging_config import setup_logging
    setup_logging(logging.DEBUG)
    test_entity_extraction()
