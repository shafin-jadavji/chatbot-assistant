from fastapi import APIRouter, Request
from pydantic import BaseModel
from services.langchain_service import chat_with_memory
from utils.logging_config import get_logger
import os

# Get logger for this module
logger = get_logger(__name__)

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    test_ip: str = None  # Optional field to override IP for testing

@router.post("/chat")
async def chat_endpoint(request: ChatRequest, req: Request):
    logger.info(f"Received message: {request.message}")
    
    # Get client IP address or use test_ip if provided
    client_ip = request.test_ip if request.test_ip else req.client.host
    logger.debug(f"Using IP: {client_ip}")

    try:
        response = chat_with_memory(request.message, client_ip=client_ip)
        logger.info(f"OpenAI Response: {response}")
        return {"response": response}
    except Exception as e:
        logger.error(f"Error in chat endpoint: {str(e)}", exc_info=True)
        return {"error": "Internal Server Error"}