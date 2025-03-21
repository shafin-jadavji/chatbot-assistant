import os
import sys
import requests
from datetime import datetime
from typing import List, Dict, Any, Optional

# Add the project root directory to Python path when running directly
if __name__ == "__main__":
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_config import get_logger
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get logger for this module
logger = get_logger(__name__)

# News API key from environment variables
NEWS_API_KEY = os.getenv("NEWS_API_KEY")

if not NEWS_API_KEY:
    logger.warning("NEWS_API_KEY not found in environment variables")

class NewsService:
    """Service for fetching news from NewsAPI.org"""
    
    BASE_URL = "https://newsapi.org/v2"
    
    @staticmethod
    def get_top_headlines(
        country: str = "us", 
        category: Optional[str] = None,
        query: Optional[str] = None,
        page_size: int = 5
    ) -> Dict[str, Any]:
        """
        Fetch top headlines from NewsAPI
        
        Args:
            country: Country code (default: "us")
            category: News category (business, entertainment, health, science, sports, technology)
            query: Search term
            page_size: Number of results to return (default: 5)
            
        Returns:
            Dict containing news articles
        """
        endpoint = f"{NewsService.BASE_URL}/top-headlines"
        
        params = {
            "apiKey": NEWS_API_KEY,
            "country": country,
            "pageSize": page_size
        }
        
        if category:
            params["category"] = category
            
        if query:
            params["q"] = query
            
        logger.info(f"Fetching news: country={country}, category={category}, query={query}")
        
        try:
            response = requests.get(endpoint, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("status") == "ok":
                logger.info(f"Successfully fetched {len(data.get('articles', []))} news articles")
                return data
            else:
                logger.error(f"News API error: {data.get('message', 'Unknown error')}")
                return {"error": data.get("message", "Failed to fetch news")}
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Request error fetching news: {str(e)}")
            return {"error": f"Failed to fetch news: {str(e)}"}
        except Exception as e:
            logger.error(f"Unexpected error fetching news: {str(e)}")
            return {"error": f"An unexpected error occurred: {str(e)}"}            
    @staticmethod
    def format_news_response(news_data: Dict[str, Any]) -> str:
        """
        Format news data into a readable response
        
        Args:
            news_data: News data from the API
            
        Returns:
            Formatted news string
        """
        if "error" in news_data:
            return f"Sorry, I couldn't fetch the news: {news_data['error']}"
            
        articles = news_data.get("articles", [])
        
        if not articles:
            return "I couldn't find any news articles matching your request."
            
        response = "Here are the latest headlines:\n\n"
        
        for i, article in enumerate(articles[:5], 1):
            title = article.get("title", "No title")
            source = article.get("source", {}).get("name", "Unknown source")
            url = article.get("url", "")
            
            response += f"{i}. {title} ({source})\n"
            if url:
                response += f"   Read more: {url}\n"
            response += "\n"
            
        return response

def get_news(category: Optional[str] = None, query: Optional[str] = None) -> str:
    """
    Get formatted news based on category or query
    
    Args:
        category: News category
        query: Search term
        
    Returns:
        Formatted news string
    """
    news_data = NewsService.get_top_headlines(category=category, query=query)
    return NewsService.format_news_response(news_data)

# --- TEST FUNCTION ---
def test_news_service():
    logger.info("Starting news service test")
    
    # Test general headlines
    logger.info("Testing general headlines")
    general_news = get_news()
    logger.info(f"General news response:\n{general_news}")
    
    # Test category
    logger.info("Testing technology category")
    tech_news = get_news(category="technology")
    logger.info(f"Technology news response:\n{tech_news}")
    
    # Test query
    logger.info("Testing query 'climate'")
    query_news = get_news(query="climate")
    logger.info(f"Climate news response:\n{query_news}")
    
    logger.info("News service test completed")

if __name__ == "__main__":
    # Import and setup logging when running this file directly
    from utils.logging_config import setup_logging
    import logging
    setup_logging(logging.DEBUG)
    test_news_service()
