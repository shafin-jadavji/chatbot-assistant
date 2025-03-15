from fastapi import APIRouter
from pydantic import BaseModel
from services.openai_service import get_chatbot_response

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Received message: {request.message}")  # Debugging

    try:
        response = get_chatbot_response(request.message)
        print(f"📤 OpenAI Response: {response}")  # Debugging
        return {"response": response}
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return {"error": "Internal Server Error"}

