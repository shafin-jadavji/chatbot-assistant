import os
import sys

# Add the project root directory to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from utils.logging_config import get_logger

from services.intent_service import detect_intent, detect_news_category, extract_news_query, detect_temperature_unit
from services.entity_service import extract_entities
from services.news_service import get_news
from services.weather_service import get_weather
from services.geolocation_service import get_location_from_ip
from config import DEFAULT_WEATHER_LOCATION

# Get logger for this module
logger = get_logger(__name__)

# Load environment variables
load_dotenv()

# Initialize LangChain OpenAI model
llm = ChatOpenAI(
    model_name="gpt-4",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

logger.info("Initialized LangChain OpenAI model")

# Memory store for conversation context (this will be improved in future phases)
conversation_history = []

def handle_weather_request(entities, user_message, client_ip=None):
    """
    Handles weather-related queries by extracting location entities and temperature unit preference.
    
    Args:
        entities (dict): Extracted entities from the message
        user_message (str): The original user message
        client_ip (str, optional): Client IP address for geolocation if no location provided
        
    Returns:
        str: Weather response
    """
    location = entities.get("GPE")
    
    # If no location is provided, try to use the default location
    if not location:
        if DEFAULT_WEATHER_LOCATION:
            location = [DEFAULT_WEATHER_LOCATION]
            logger.info(f"No location provided, using default location: {DEFAULT_WEATHER_LOCATION}")
        # If no default location, try to get it from the client's IP
        elif client_ip:
            logger.info(f"No location provided, attempting to use client IP: {client_ip}")
            geo_data = get_location_from_ip(client_ip)
            
            if geo_data and geo_data.get("city"):
                location = [geo_data.get("city")]
                logger.info(f"Using geolocation from IP: {location[0]}")
            else:
                logger.warning("Could not determine location from IP")
                return "I need a location to fetch weather details. Please specify a city or region."
        else:
            logger.warning("Weather request received but no location entity found, no default location set, and no IP provided")
            return "I need a location to fetch weather details. Please specify a city or region."
    
    location_str = location[0] if location else "unknown location"
    logger.info(f"Weather request for location: {location_str}")
    
    # Detect temperature unit preference (defaults to imperial/Fahrenheit if not specified)
    unit_preference = detect_temperature_unit(user_message)
    unit = unit_preference if unit_preference else "imperial"
    
    # Log the unit being used
    unit_name = "Celsius" if unit == "metric" else "Fahrenheit"
    logger.info(f"Using temperature unit: {unit_name}")

    # Detect time period from entities or from the message directly
    time_period = None
    
    # First check DATE entities
    if entities.get("DATE"):
        date_entity = entities["DATE"][0].lower()
        # Normalize date entities
        if "week" in date_entity:
            time_period = "week"
        elif "today" in date_entity:
            time_period = "today" if "later" not in date_entity else "later today"
        elif "tomorrow" in date_entity:
            time_period = "tomorrow"
        else:
            time_period = date_entity
        logger.info(f"Using time period from DATE entity: {time_period}")
    # Then check TIME entities
    elif entities.get("TIME"):
        time_period = entities["TIME"][0].lower()
        logger.info(f"Using time period from TIME entity: {time_period}")
    # Finally, try to detect from the message
    else:
        from services.intent_service import detect_time_period
        time_period, _ = detect_time_period(user_message)
        if time_period:
            logger.info(f"Using time period detected from message: {time_period}")
    
    # Fetch weather data using the weather service with the specified unit and time period
    weather_response = get_weather(location_str, unit, time_period)
    logger.info(f"Weather response: {weather_response}")
    return weather_response

def handle_news_request(user_message):
    """
    Handles news-related queries by detecting category and query.
    
    Args:
        user_message (str): The user's input message
        
    Returns:
        str: News response
    """
    logger.info("News request received")
    
    # Extract category and query from the message
    category = detect_news_category(user_message)
    query = extract_news_query(user_message)
    
    logger.info(f"News request with category: {category}, query: {query}")
    
    # Get news based on category and query
    news_response = get_news(category=category, query=query)
    
    # Return the news response
    return news_response

def handle_stocks_request(entities):
    """
    Placeholder for future stocks-related queries.
    """
    logger.info("Stocks request received - functionality not yet implemented")
    return "I'll be able to provide stock information in a future update."

def chat_with_memory(user_message, client_ip=None):
    """
    Handles conversation with memory, integrates intent detection and entity extraction,
    and routes specific intents to appropriate handlers.
    
    Args:
        user_message (str): The user's input message
        client_ip (str, optional): Client IP address for geolocation
    """
    logger.debug(f"Processing user message: '{user_message}'")
    
    # Extract intent and entities
    intent = detect_intent(user_message)
    entities = extract_entities(user_message, intent=intent)

    # Log extracted details
    logger.info(f"Detected intent: {intent}, Extracted entities: {entities}")

    # Intent-based routing to avoid unnecessary OpenAI calls
    if intent == "weather":
        logger.debug("Routing to weather handler")
        return handle_weather_request(entities, user_message, client_ip=client_ip)
    
    if intent == "news":
        logger.debug("Routing to news handler")
        return handle_news_request(user_message)
        
    if intent == "stocks":
        logger.debug("Routing to stocks handler")
        return handle_stocks_request(entities)

    # Append user message to conversation history
    conversation_history.append(HumanMessage(content=user_message))
    logger.debug("Added user message to conversation history")

    # Generate AI response using OpenAI only when necessary
    logger.debug("Generating AI response using LangChain")
    response = llm.invoke(conversation_history)

    # Store AI response
    conversation_history.append(AIMessage(content=response.content))
    logger.debug("Added AI response to conversation history")

    return response.content

def test_weather_handling():
    """
    Functional test for weather handling functionality.
    This can be run directly without starting the full service.
    """
    logger.info("Starting weather handling test")
    
    test_cases = [
        {"message": "What's the weather in Phoenix?", "expected_intent": "weather", "expected_location": "Phoenix"},
        {"message": "What's the weather in New York tomorrow?", "expected_intent": "weather", "expected_location": "New York", "expected_time": "tomorrow"},
        {"message": "What's the weather for the week in Seattle?", "expected_intent": "weather", "expected_location": "Seattle", "expected_time": "week"},
        {"message": "What's the weather on Monday in Chicago?", "expected_intent": "weather", "expected_location": "Chicago", "expected_time": "monday"},
        {"message": "What's the temperature in London in Celsius?", "expected_intent": "weather", "expected_location": "London", "expected_unit": "metric"},
    ]
    
    for i, test in enumerate(test_cases):
        logger.info(f"Test {i+1}/{len(test_cases)}: {test['message']}")
        
        # Test intent detection
        intent = detect_intent(test["message"])
        assert intent == test["expected_intent"], f"Expected intent {test['expected_intent']}, got {intent}"
        
        # Test entity extraction
        entities = extract_entities(test["message"], intent=intent)
        
        # Check location
        if "expected_location" in test:
            locations = entities.get("GPE", [])
            assert any(test["expected_location"] in loc for loc in locations), f"Expected location {test['expected_location']} not found in {locations}"
        
        # Test weather handling
        response = handle_weather_request(entities, test["message"])
        logger.info(f"Response: {response}")
        
        # Basic validation of response
        assert response and len(response) > 20, "Response too short or empty"
        
        if "expected_location" in test:
            assert test["expected_location"] in response, f"Response doesn't contain expected location {test['expected_location']}"
    
    logger.info("All weather handling tests passed!")

def test_news_handling():
    """
    Functional test for news handling functionality.
    """
    logger.info("Starting news handling test")
    
    test_cases = [
        {"message": "What's the latest news?", "expected_intent": "news"},
        {"message": "Tell me about technology news", "expected_intent": "news", "expected_category": "technology"},
        {"message": "Show me news about climate change", "expected_intent": "news", "expected_query": "climate change"},
    ]
    
    for i, test in enumerate(test_cases):
        logger.info(f"Test {i+1}/{len(test_cases)}: {test['message']}")
        
        # Test intent detection
        intent = detect_intent(test["message"])
        assert intent == test["expected_intent"], f"Expected intent {test['expected_intent']}, got {intent}"
        
        # Test news handling
        response = handle_news_request(test["message"])
        logger.info(f"Response: {response}")
        
        # Basic validation of response
        assert response and len(response) > 20, "Response too short or empty"
    
    logger.info("All news handling tests passed!")

if __name__ == "__main__":
    # This allows running tests directly by executing this file
    import logging
    from utils.logging_config import setup_logging
    
    # Set up logging with higher level for testing
    setup_logging(logging.INFO)
    
    # Run the tests
    try:
        test_weather_handling()
        test_news_handling()
        logger.info("All functional tests passed!")
    except AssertionError as e:
        logger.error(f"Test failed: {str(e)}")
