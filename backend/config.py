import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(f"*** OPENAI KEY: {OPENAI_API_KEY} ***") 

# Default location for weather requests when no location is specified
DEFAULT_WEATHER_LOCATION = os.getenv("DEFAULT_WEATHER_LOCATION", "Phoenix")
