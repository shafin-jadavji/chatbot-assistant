import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage

from services.intent_service import detect_intent
from services.entity_service import extract_entities

# Load environment variables
load_dotenv()

# Initialize LangChain OpenAI model
llm = ChatOpenAI(
    model_name="gpt-4",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Memory store for conversation context (this will be improved in future phases)
conversation_history = []

def handle_weather_request(entities):
    """
    Handles weather-related queries by extracting location entities.
    """
    location = entities.get("GPE")
    if location:
        return f"Fetching weather information for {location}..."
    return "I need a location to fetch weather details."

def handle_news_request():
    """
    Handles news-related queries.
    """
    return "Fetching the latest news updates..."

def chat_with_memory(user_message):
    """
    Handles conversation with memory, integrates intent detection and entity extraction,
    and routes specific intents to appropriate handlers.
    """
    # Extract intent and entities
    intent = detect_intent(user_message)
    entities = extract_entities(user_message)

    # Log extracted details
    print(f"🔍 Intent: {intent}, 🎯 Entities: {entities}")

    # Intent-based routing
    if intent == "weather":
        return handle_weather_request(entities)
    
    if intent == "news":
        return handle_news_request()

    # Append user message to conversation history
    conversation_history.append(HumanMessage(content=user_message))

    # Generate AI response using OpenAI only when necessary
    response = llm.invoke(conversation_history)

    # Store AI response
    conversation_history.append(AIMessage(content=response.content))

    return response.content
