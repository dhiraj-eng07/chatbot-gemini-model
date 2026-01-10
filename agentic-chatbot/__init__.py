"""
Root package initialization for agentic-chatbot.
"""

__version__ = "1.0.0"
__author__ = "Your Name"
__description__ = "An agentic chatbot powered by Google Gemini and MongoDB"

from config import Config
from database import MongoDBHandler
from agents import QueryAgent, GeminiHandler

__all__ = [
    "Config",
    "MongoDBHandler",
    "QueryAgent",
    "GeminiHandler",
]
