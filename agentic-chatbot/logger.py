"""
Logging configuration for the agentic chatbot application.
"""

import logging
import sys
from config import Config


def setup_logging():
    """Configure logging for the application."""
    
    log_level = getattr(logging, Config.LOG_LEVEL, logging.INFO)
    
    # Create logger
    logger = logging.getLogger(__name__)
    logger.setLevel(log_level)
    
    # Create console handler with a higher log level
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(log_level)
    
    # Create formatter and add it to the handlers
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_handler.setFormatter(formatter)
    
    # Add handlers to the logger
    if not logger.handlers:
        logger.addHandler(console_handler)
    
    return logger


# Create global logger instance
logger = setup_logging()
