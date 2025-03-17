import os
import sys
import requests

# Add the project root directory to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from utils.logging_config import get_logger

# Load environment variables
load_dotenv()

# Get logger for this module
logger = get_logger(__name__)

WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")

def get_weather(city):
    """
    Fetch real-time weather data for a given city.
    """
    if not WEATHER_API_KEY:
        logger.error("Weather API key is missing")
        return "Weather API key is missing. Please configure it."
  
    # Changed units=metric to units=imperial for Fahrenheit
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units=imperial"
    logger.info(f"Fetching weather for {city} from API")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise error if API call fails
        data = response.json()

        if "weather" in data and "main" in data:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            # Changed °C to °F in the return string
            logger.info(f"Successfully retrieved weather data for {city}")
            return f"The weather in {city} is {weather_desc} with a temperature of {temp}°F."
        
        logger.warning(f"Incomplete weather data received for {city}")
        return "Weather data is unavailable for this location."
    
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            logger.warning(f"City not found: {city}")
            return f"Could not find weather data for '{city}'. Please check the city name."
        logger.error(f"HTTP Error when fetching weather for {city}: {http_err}")
        return f"HTTP Error: {http_err}"
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception when fetching weather for {city}: {e}")
        return "There was an issue connecting to the weather service. Try again later."

# --- TEST FUNCTION ---
def test_weather_service():
    logger.info("Starting weather service test")
    test_cities = ["New York", "London", "Tokyo", "Mesa", "Sydney", "InvalidCity"]
    
    for city in test_cities:
        result = get_weather(city)
        logger.info(f"Weather for {city}: {result}")
    
    logger.info("Weather service test completed")

if __name__ == "__main__":
    # Import and setup logging when running this file directly
    from utils.logging_config import setup_logging
    import logging
    setup_logging(logging.DEBUG)
    test_weather_service()  # Run the test function