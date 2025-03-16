import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from utils.logging_config import get_logger

from services.intent_service import detect_intent
from services.entity_service import extract_entities

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

def handle_news_request():
    """
    Handles news-related queries.
    """
    logger.info("News request received")
    return "Fetching the latest news updates..."

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

    # Intent-based routing
    if intent == "weather":
        logger.debug("Routing to weather handler")
        return handle_weather_request(entities)
    
    if intent == "news":
        logger.debug("Routing to news handler")
        return handle_news_request()

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