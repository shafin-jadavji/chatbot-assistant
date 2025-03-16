import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
logs_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Generate log filename with timestamp
log_filename = os.path.join(logs_dir, f'chatbot_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log')

def setup_logging(default_level=logging.INFO):
    """
    Configure logging for the entire application.
    
    Args:
        default_level: Default logging level to use
    
    Returns:
        None
    """
    # Check if the root logger already has handlers to avoid duplicate logs
    root_logger = logging.getLogger()
    if root_logger.handlers:
        # If handlers exist, just set the level and return
        root_logger.setLevel(default_level)
        logging.info("Logging already configured, updating log level only")
        return
        
    # Basic configuration
    logging.basicConfig(
        level=default_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S',
        handlers=[
            # File handler for persistent logs
            logging.FileHandler(log_filename),
            # Console handler for immediate feedback
            logging.StreamHandler()
        ]
    )
    
    # Reduce verbosity of some third-party libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('spacy').setLevel(logging.WARNING)
    
    logging.info(f"Logging initialized. Log file: {log_filename}")
def get_logger(name):
    """
    Get a logger with the specified name.
    
    Args:
        name: Name for the logger, typically __name__ from the calling module
        
    Returns:
        Logger: Configured logger instance
    """
    return logging.getLogger(name)
