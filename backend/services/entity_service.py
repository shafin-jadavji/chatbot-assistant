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
    logger.info("Successfully loaded spaCy entity model 'en_core_web_sm'")
except Exception as e:
    logger.error(f"Failed to load spaCy model: {str(e)}")
    raise

# Common city names that might be misclassified as PERSON
COMMON_CITY_NAMES = [
    "mesa", "chandler", "gilbert", "tempe", "scottsdale", "glendale", 
    "peoria", "surprise", "avondale", "goodyear", "buckeye", "casa grande",
    "flagstaff", "prescott", "kingman", "bullhead city", "lake havasu city",
    "yuma", "sierra vista", "sedona", "paradise valley", "fountain hills",
    "oro valley", "marana", "sahuarita", "queen creek", "apache junction",
    "maricopa", "eloy", "coolidge", "florence", "globe", "miami", "payson",
    "show low", "snowflake", "winslow", "holbrook", "page", "williams",
    "cottonwood", "camp verde", "wickenburg", "parker", "bisbee", "douglas",
    "nogales", "safford", "thatcher", "clifton", "willcox", "benson", "tombstone"
]

def extract_entities(user_message, intent=None):
    """
    Extracts various entities from user messages using spaCy.
    Returns a dictionary where the values are lists of entities.
    
    Args:
        user_message (str): The user's input message
        intent (str, optional): The detected intent for context-aware processing
        
    Returns:
        dict: A dictionary of extracted entities
    """
    logger.debug(f"Processing message: '{user_message}'")
    
    if intent:
        logger.debug(f"Using provided intent for context-aware entity extraction: {intent}")
    
    doc = nlp(user_message)
    
    entities = {
        "GPE": [],  # Location (City, Country, etc.)
        "PERSON": [],  # Names (e.g., John, Barack Obama)
        "TIME": [],  # Time expressions (e.g., "tomorrow", "3 PM")
        "DATE": [],  # Dates (e.g., "Monday", "March 5")
        "ORG": [],  # Organizations (e.g., Google, NASA)
    }

    # First, collect all entities as normal
    for ent in doc.ents:
        if ent.label_ in entities:
            entities[ent.label_].append(ent.text)  # Store all occurrences
            logger.debug(f"Found entity: {ent.text} ({ent.label_})")
    
    # For weather intent, check for city names in PERSON entities or in the message text
    if intent == "weather":
        # Check if we have any PERSON entities that might actually be cities
        person_entities = entities["PERSON"].copy()  # Create a copy to avoid modification during iteration
        for person in person_entities:
            if person.lower() in COMMON_CITY_NAMES:
                logger.info(f"Reclassifying '{person}' from PERSON to GPE based on common city names list")
                entities["GPE"].append(person)
                # Remove from PERSON list
                entities["PERSON"].remove(person)
        
        # If still no GPE, look for city names in the message text
        if not entities["GPE"]:
            message_lower = user_message.lower()
            
            # Look for patterns like "in X", "for X", "at X" where X might be a city
            location_indicators = ["in ", "for ", "at ", "near "]
            for indicator in location_indicators:
                if indicator in message_lower:
                    parts = message_lower.split(indicator, 1)
                    if len(parts) > 1:
                        potential_location = parts[1].strip().split()[0]  # Get first word after indicator
                        
                        # Check if it's in our common city names list
                        for city in COMMON_CITY_NAMES:
                            if city.startswith(potential_location) or potential_location.startswith(city):
                                logger.info(f"Found potential city '{city}' in message text")
                                entities["GPE"].append(city.title())  # Add with proper capitalization
                                break
    
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
        "Is Phoenix a city in Arizona?",  # {"GPE": ["Phoenix", "Arizona"]}
        "What's the weather in Mesa?",  # Should detect Mesa as GPE
        "What's the weather in Chandler?",  # Should detect Chandler as GPE
        "Tell me about John Smith",  # Should keep John Smith as PERSON
        "What's the weather in Gilbert today?",  # Should detect Gilbert as GPE and today as DATE
    ]

    # Test with different intents
    intents = {
        "What's the weather in Phoenix?": "weather",
        "What's the weather in Mesa?": "weather",
        "What's the weather in Chandler?": "weather",
        "What's the weather in Gilbert today?": "weather",
        "What is the temperature in London?": "weather",
        "Tell me about John Smith": "general",
        "Barack Obama was the 44th President of the United States.": "general",
        "I have a meeting on Monday at 3 PM.": "general",
        "Google is one of the biggest tech companies.": "general",
        "Is Phoenix a city in Arizona?": "general"
    }

    for i, message in enumerate(test_messages):
        logger.info(f"Test {i+1}/{len(test_messages)}: Processing '{message}'")
        intent = intents.get(message, "general")
        entities = extract_entities(message, intent=intent)

        # Replace print with logging
        logger.info(f"Message: {message} -> Intent: {intent} -> Entities: {entities}")
    
    logger.info("Entity extraction test completed")

if __name__ == "__main__":
    # Import and setup logging when running this file directly
    from utils.logging_config import setup_logging
    setup_logging(logging.DEBUG)
    test_entity_extraction()