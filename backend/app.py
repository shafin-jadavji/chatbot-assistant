from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes.chat import router as chat_router
from utils.logging_config import setup_logging
import logging

# Initialize logging first thing
setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting Chatbot API application")

app = FastAPI()

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info("CORS middleware configured")

# Include only chat router (weather is now handled by LangChain)
app.include_router(chat_router)
logger.info("Chat router registered")

# Root endpoint
@app.get("/")
def home():
    logger.debug("Root endpoint accessed")
    return {"message": "Chatbot API is running with LangChain Agents!"}

# Log when the application is fully loaded
logger.info("Chatbot API application is ready")