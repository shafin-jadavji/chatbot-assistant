from fastapi import APIRouter
from pydantic import BaseModel
from services.langchain_service import chat_with_memory

router = APIRouter()

class ChatRequest(BaseModel):
    message: str

@router.post("/chat")
async def chat_endpoint(request: ChatRequest):
    print(f"📩 Received message: {request.message}")  # Debugging

    try:
        response = chat_with_memory(request.message)
        print(f"📤 OpenAI Response: {response}")  # Debugging
        return {"response": response}
    except Exception as e:
        print(f"❌ Error in chat endpoint: {e}")
        return {"error": "Internal Server Error"}

