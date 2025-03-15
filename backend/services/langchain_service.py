import os
from langchain_openai import ChatOpenAI
from langchain.schema import SystemMessage, HumanMessage, AIMessage
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize LangChain OpenAI model
llm = ChatOpenAI(
    model_name="gpt-4",
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

# Memory store for context (Simple Python List for now)
conversation_history = []

def chat_with_memory(user_message):
    """
    Handles conversation with memory using LangChain.
    """
    # Append user message to memory
    conversation_history.append(HumanMessage(content=user_message))
    
    # Generate AI response
    response = llm.invoke(conversation_history)
    
    # Store AI response
    conversation_history.append(AIMessage(content=response.content))
    
    return response.content
