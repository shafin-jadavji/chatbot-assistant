import os
import sys
import requests

# Add the project root directory to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_config import get_logger

# Get logger for this module
logger = get_logger(__name__)

def get_location_from_ip(ip_address):
    """
    Get location information from an IP address using ipinfo.io
    
    Args:
        ip_address (str): The IP address to lookup
        
    Returns:
        dict: Location information including city, country, etc. or None if failed
    """
    logger.info(f"Attempting to get location from IP: {ip_address}")
    
    try:
        # Using ipinfo.io as a free geolocation service
        response = requests.get(f"https://ipinfo.io/{ip_address}/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        
        logger.info(f"Successfully retrieved location data for IP: {ip_address}")
        return {
            "city": data.get("city"),
            "region": data.get("region"),
            "country": data.get("country"),
            "loc": data.get("loc")  # Latitude,Longitude
        }
    except Exception as e:
        logger.error(f"Error getting location from IP: {str(e)}")
        return None

# --- TEST FUNCTION ---
def test_geolocation_service():
    """
    Test function to validate the geolocation service with real API calls.
    Can be run directly to verify the service is working correctly.
    """
    logger.info("Starting geolocation service test")
    
    # Test with some well-known IP addresses
    test_ips = [
        "8.8.8.8",        # Google DNS - City: Mountain View, Region: California, Country: US, Approximate coordinates: 37.4056,-122.0775
        "119.29.29.29",    # DNSPod Public DNS (China) - City=Guangzhou, Region=Guangdong, Country=CN, Approximate coordinates: 23.1291,113.2644
        "103.86.96.100",   # APNIC Research (Australia) - City=Sydney, Region=New South Wales, Country=AU, Approximate coordinates: -33.8651,151.2099
        "208.67.222.222", # OpenDNS - City: San Francisco, Region: California, Country: US, Approximate coordinates: 37.7697,-122.3933
        "68.98.8.91",
        "invalid_ip"      # Invalid IP to test error handling - This will trigger an error as it's not a valid IP address format
    ]

    for ip in test_ips:
        logger.info(f"Testing geolocation for IP: {ip}")
        result = get_location_from_ip(ip)
        
        if result:
            logger.info(f"Location for {ip}: City={result.get('city')}, "
                        f"Region={result.get('region')}, Country={result.get('country')}, Approximate coordinates={result.get('loc')}")
        else:
            logger.warning(f"Could not retrieve location for IP: {ip}")
    
    logger.info("Geolocation service test completed")

if __name__ == "__main__":
    # Import and setup logging when running this file directly
    from utils.logging_config import setup_logging
    import logging
    setup_logging(logging.DEBUG)
    test_geolocation_service()  # Run the test function