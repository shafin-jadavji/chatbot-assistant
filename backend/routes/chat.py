from fastapi import APIRouter
from pydantic import BaseModel
from services.langchain_service import chat_with_memory
from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    logger.info(f"Received message: {request.message}")

    try:
        response = chat_with_memory(request.message)
        logger.info(f"OpenAI Response: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return {"error": "Internal Server Error"}
