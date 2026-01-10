import os
import re
from dotenv import load_dotenv
from urllib.parse import urlparse

load_dotenv()

class Config:
    # MongoDB Configuration
    MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017/").strip('"').strip("'")
    
    # Extract database name from URI
    @staticmethod
    def extract_db_name(uri):
        try:
            parsed = urlparse(uri)
            if parsed.path and parsed.path != '/':
                db_name = parsed.path.lstrip('/').split('/')[0]
                return db_name if db_name else "chatbot_db"
            return "chatbot_db"
        except:
            return "chatbot_db"
    
    DATABASE_NAME = os.getenv("DATABASE_NAME") or extract_db_name(MONGO_URI)
    
    # Gemini AI Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "").strip('"').strip("'")
    
    # Application Configuration
    DEBUG = os.getenv("DEBUG", "True").lower() == "true"
    PORT = int(os.getenv("PORT", 5000))
    
    # Collection names
    USER_COLLECTION = "users"
    PRODUCT_COLLECTION = "products"
    ORDERS_COLLECTION = "orders"
    CONVERSATIONS_COLLECTION = "conversations"

config = Config()