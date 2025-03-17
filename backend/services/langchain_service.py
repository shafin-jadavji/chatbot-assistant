import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from utils.logging_config import get_logger

from services.intent_service import detect_intent, detect_news_category, extract_news_query
from services.entity_service import extract_entities
from services.news_service import get_news

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

def handle_weather_request(entities):
    """
    Handles weather-related queries by extracting location entities.
    """
    location = entities.get("GPE")
    if location:
        location_str = location[0] if location else "unknown location"
        logger.info(f"Weather request for location: {location_str}")
        return f"Fetching weather information for {location_str}..."
    logger.warning("Weather request received but no location entity found")
    return "I need a location to fetch weather details."

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
    
    return news_response

def handle_stocks_request(entities):
    """
    Placeholder for future stocks-related queries.
    """
    logger.info("Stocks request received - functionality not yet implemented")
    return "I'll be able to provide stock information in a future update."

def chat_with_memory(user_message):
    """
    Handles conversation with memory, integrates intent detection and entity extraction,
    and routes specific intents to appropriate handlers.
    """
    logger.debug(f"Processing user message: '{user_message}'")
    
    # Extract intent and entities
    intent = detect_intent(user_message)
    entities = extract_entities(user_message)

    # Log extracted details
    logger.info(f"Detected intent: {intent}, Extracted entities: {entities}")

    # Intent-based routing to avoid unnecessary OpenAI calls
    if intent == "weather":
        logger.debug("Routing to weather handler")
        return handle_weather_request(entities)
    
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