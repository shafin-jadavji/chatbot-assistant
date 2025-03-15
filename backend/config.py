import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# print(f"*** OPENAI KEY: {OPENAI_API_KEY} ***") 
