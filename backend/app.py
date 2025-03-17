from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from utils.logging_config import setup_logging
import logging
import os

# Initialize logging first thing
setup_logging()
logger = logging.getLogger(__name__)

logger.info("Starting Chatbot API application")

# Import services explicitly to initialize them at startup
logger.info("Importing service modules...")
from routes.chat import router as chat_router
from services import entity_service, intent_service, langchain_service

app = FastAPI()

# Get allowed origins from environment variable or use defaults
allowed_origins = os.environ.get(
    "ALLOWED_ORIGINS", 
    "http://localhost:5173,http://localhost:5174,http://localhost:3000,http://localhost:8080"
).split(",")

logger.info(f"Configuring CORS for origins: {allowed_origins}")

# Enable CORS for frontend communication
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,  # Allow multiple frontend ports
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