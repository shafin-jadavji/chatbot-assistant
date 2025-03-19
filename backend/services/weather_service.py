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

def get_weather(city, unit="imperial"):
    """
    Fetch real-time weather data for a given city.
    
    Args:
        city (str): The city to get weather for
        unit (str): The temperature unit - "imperial" for Fahrenheit or "metric" for Celsius
        
    Returns:
        str: Weather information formatted as a string
    """
    if not WEATHER_API_KEY:
        logger.error("Weather API key is missing")
        return "Weather API key is missing. Please configure it."
  
    # Use the unit parameter to determine which unit to request
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units={unit}"
    logger.info(f"Fetching weather for {city} from API (unit: {unit})")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()  # Raise error if API call fails
        data = response.json()

        if "weather" in data and "main" in data:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            # Use the correct temperature symbol based on the unit
            temp_symbol = "°F" if unit == "imperial" else "°C"
            logger.info(f"Successfully retrieved weather data for {city}")
            return f"The weather in {city} is {weather_desc} with a temperature of {temp}{temp_symbol}."
        
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
    test_cities = ["New York", "London", "Tokyo", "InvalidCity"]
    
    for city in test_cities:
        # Test with both units
        result_f = get_weather(city, "imperial")
        logger.info(f"Weather for {city} (Fahrenheit): {result_f}")
        
        result_c = get_weather(city, "metric")
        logger.info(f"Weather for {city} (Celsius): {result_c}")

        # test when no unit is specified
        result = get_weather(city)
        logger.info(f"Weather for {city} (Default): {result}")
    
    logger.info("Weather service test completed")

if __name__ == "__main__":
    # Import and setup logging when running this file directly
    from utils.logging_config import setup_logging
    import logging
    setup_logging(logging.DEBUG)
    test_weather_service()  # Run the test function