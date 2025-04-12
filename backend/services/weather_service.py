import os
import sys
import requests
from datetime import datetime, timedelta

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

def get_weather(city, unit="imperial", time_period=None):
    """
    Fetch weather data for a given city and time period.
    
    Args:
        city (str): The city to get weather for
        unit (str): The temperature unit - "imperial" for Fahrenheit or "metric" for Celsius
        time_period (str, optional): Time period for forecast (e.g., "today", "tomorrow", "week")
        
    Returns:
        str: Weather information formatted as a string
    """
    if not WEATHER_API_KEY:
        logger.error("Weather API key is missing")
        return "Weather API key is missing. Please configure it."
    
    # If no time period or "now" is specified, get current weather
    if not time_period or time_period.lower() in ["now", "current"]:
        return get_current_weather(city, unit)
    
    # For future forecasts, use the forecast endpoint
    return get_forecast_weather(city, unit, time_period)

def get_current_weather(city, unit="imperial"):
    """
    Fetch current weather data for a given city.
    
    Args:
        city (str): The city to get weather for
        unit (str): The temperature unit - "imperial" for Fahrenheit or "metric" for Celsius
        
    Returns:
        str: Current weather information formatted as a string
    """
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={WEATHER_API_KEY}&units={unit}"
    logger.info(f"Fetching current weather for {city} from API (unit: {unit})")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "weather" in data and "main" in data:
            weather_desc = data["weather"][0]["description"]
            temp = data["main"]["temp"]
            temp_symbol = "°F" if unit == "imperial" else "°C"
            feels_like = data["main"]["feels_like"]
            humidity = data["main"]["humidity"]
            
            logger.info(f"Successfully retrieved current weather data for {city}")
            return (f"The current weather in {city} is {weather_desc} with a temperature of "
                   f"{temp}{temp_symbol} (feels like {feels_like}{temp_symbol}). "
                   f"Humidity is {humidity}%.")
        
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

def get_forecast_weather(city, unit="imperial", time_period="tomorrow"):
    """
    Fetch forecast weather data for a given city and time period.
    
    Args:
        city (str): The city to get weather for
        unit (str): The temperature unit - "imperial" for Fahrenheit or "metric" for Celsius
        time_period (str): Time period for forecast (e.g., "today", "tomorrow", "week")
        
    Returns:
        str: Forecast weather information formatted as a string
    """
    # 5-day forecast with 3-hour intervals
    url = f"https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={WEATHER_API_KEY}&units={unit}"
    logger.info(f"Fetching forecast for {city} from API (unit: {unit}, time_period: {time_period})")

    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()

        if "list" not in data or not data["list"]:
            logger.warning(f"No forecast data available for {city}")
            return f"No forecast data available for {city}."

        # Get the forecast data based on the requested time period
        forecast_data = parse_forecast_data(data["list"], time_period, unit, city)
        
        if not forecast_data:
            logger.warning(f"Could not generate forecast for time period: {time_period}")
            return f"I couldn't generate a forecast for {time_period} in {city}. Try asking for today, tomorrow, or the week."
        
        logger.info(f"Successfully retrieved forecast data for {city} ({time_period})")
        return forecast_data
    
    except requests.exceptions.HTTPError as http_err:
        if response.status_code == 404:
            logger.warning(f"City not found: {city}")
            return f"Could not find forecast data for '{city}'. Please check the city name."
        logger.error(f"HTTP Error when fetching forecast for {city}: {http_err}")
        return f"HTTP Error: {http_err}"
    
    except requests.exceptions.RequestException as e:
        logger.error(f"Request exception when fetching forecast for {city}: {e}")
        return "There was an issue connecting to the weather service. Try again later."

def parse_forecast_data(forecast_list, time_period, unit, city):
    """
    Parse the forecast data based on the requested time period.
    
    Args:
        forecast_list (list): List of forecast data points
        time_period (str): Time period for forecast (e.g., "today", "tomorrow", "week")
        unit (str): The temperature unit - "imperial" for Fahrenheit or "metric" for Celsius
        city (str): City name to include in the response
        
    Returns:
        str: Formatted forecast information
    """
    temp_symbol = "°F" if unit == "imperial" else "°C"
    now = datetime.now()
    time_period = time_period.lower() if time_period else "now"
    
    # Handle different time periods
    if time_period in ["today", "later today"]:
        return format_day_forecast(forecast_list, now, temp_symbol, "Today", city)
    
    elif time_period in ["tomorrow"]:
        tomorrow = now + timedelta(days=1)
        return format_day_forecast(forecast_list, tomorrow, temp_symbol, "Tomorrow", city)
    
    elif time_period in ["week", "this week", "next 5 days", "5 day", "5-day"]:
        return format_week_forecast(forecast_list, now, temp_symbol, city)
    
    # Handle specific days of the week
    days_of_week = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    if time_period in days_of_week:
        target_day_idx = days_of_week.index(time_period)
        current_day_idx = now.weekday()
        
        # Calculate days to add (if today is the target day, look for next week)
        days_to_add = (target_day_idx - current_day_idx) % 7
        if days_to_add == 0:
            days_to_add = 7  # Next week's same day
        
        target_date = now + timedelta(days=days_to_add)
        return format_day_forecast(forecast_list, target_date, temp_symbol, time_period.capitalize(), city)
    
    # Default to tomorrow if time period is not recognized
    logger.warning(f"Unrecognized time period: {time_period}, defaulting to tomorrow")
    tomorrow = now + timedelta(days=1)
    return format_day_forecast(forecast_list, tomorrow, temp_symbol, "Tomorrow", city)

def format_day_forecast(forecast_list, target_date, temp_symbol, day_label, city):
    """
    Format forecast for a specific day.
    
    Args:
        forecast_list (list): List of forecast data points
        target_date (datetime): Target date for forecast
        temp_symbol (str): Temperature symbol (°F or °C)
        day_label (str): Label for the day (e.g., "Today", "Tomorrow")
        city (str): City name to include in the response
        
    Returns:
        str: Formatted day forecast
    """
    # Filter forecast items for the target date
    target_items = [
        item for item in forecast_list 
        if datetime.fromtimestamp(item["dt"]).date() == target_date.date()
    ]
    
    if not target_items:
        return f"No forecast data available for {day_label.lower()} in {city}."
    
    # Group by morning, afternoon, evening
    morning = [item for item in target_items if 6 <= datetime.fromtimestamp(item["dt"]).hour < 12]
    afternoon = [item for item in target_items if 12 <= datetime.fromtimestamp(item["dt"]).hour < 18]
    evening = [item for item in target_items if 18 <= datetime.fromtimestamp(item["dt"]).hour < 24]
    
    # Format the response
    response = f"{day_label}'s forecast for {city}: "
    
    if morning:
        avg_temp = sum(item["main"]["temp"] for item in morning) / len(morning)
        main_weather = max(set(item["weather"][0]["main"] for item in morning), key=[item["weather"][0]["main"] for item in morning].count)
        response += f"Morning: {main_weather}, {avg_temp:.1f}{temp_symbol}. "
    
    if afternoon:
        avg_temp = sum(item["main"]["temp"] for item in afternoon) / len(afternoon)
        main_weather = max(set(item["weather"][0]["main"] for item in afternoon), key=[item["weather"][0]["main"] for item in afternoon].count)
        response += f"Afternoon: {main_weather}, {avg_temp:.1f}{temp_symbol}. "
    
    if evening:
        avg_temp = sum(item["main"]["temp"] for item in evening) / len(evening)
        main_weather = max(set(item["weather"][0]["main"] for item in evening), key=[item["weather"][0]["main"] for item in evening].count)
        response += f"Evening: {main_weather}, {avg_temp:.1f}{temp_symbol}."
    
    return response

def format_week_forecast(forecast_list, start_date, temp_symbol, city):
    """
    Format forecast for the next 5 days.
    
    Args:
        forecast_list (list): List of forecast data points
        start_date (datetime): Start date for forecast
        temp_symbol (str): Temperature symbol (°F or °C)
        city (str): City name to include in the response
        
    Returns:
        str: Formatted week forecast
    """
    # Group forecast items by day
    day_forecasts = {}
    
    for item in forecast_list:
        item_date = datetime.fromtimestamp(item["dt"]).date()
        if item_date >= start_date.date() and (item_date - start_date.date()).days < 5:
            if item_date not in day_forecasts:
                day_forecasts[item_date] = []
            day_forecasts[item_date].append(item)
    
    if not day_forecasts:
        return f"No forecast data available for the next 5 days in {city}."
    
    # Format the response
    response = f"5-day forecast for {city}: "
    
    for day, items in sorted(day_forecasts.items()):
        day_name = day.strftime("%A")
        avg_temp = sum(item["main"]["temp"] for item in items) / len(items)
        main_weather = max(set(item["weather"][0]["main"] for item in items), key=[item["weather"][0]["main"] for item in items].count)
        response += f"{day_name}: {main_weather}, {avg_temp:.1f}{temp_symbol}. "
    
    return response.strip()

# --- TEST FUNCTION ---
def test_weather_service():
    logger.info("Starting weather service test")
    test_cities = ["New York", "London", "Tokyo"]
    test_time_periods = ["now", "today", "tomorrow", "week", "monday"]
    
    for city in test_cities:
        # Test current weather
        result = get_weather(city, "imperial")
        logger.info(f"Current weather for {city} (Fahrenheit): {result}")
        
        # Test forecasts with different time periods
        for time_period in test_time_periods:
            result = get_weather(city, "imperial", time_period)
            logger.info(f"Weather for {city} ({time_period}): {result}")
    
    # Test specific examples
    specific_tests = [
        ("New York", "imperial", "tomorrow"),
        ("London", "metric", "week"),
        ("Tokyo", "metric", "monday"),
        ("Phoenix", "imperial", "later today"),
    ]
    
    for city, unit, time_period in specific_tests:
        result = get_weather(city, unit, time_period)
        unit_name = "Celsius" if unit == "metric" else "Fahrenheit"
        logger.info(f"Weather for {city} ({time_period}, {unit_name}): {result}")
    
    logger.info("Weather service test completed")

if __name__ == "__main__":
    # Import and setup logging when running this file directly
    from utils.logging_config import setup_logging
    import logging
    setup_logging(logging.DEBUG)
    test_weather_service()