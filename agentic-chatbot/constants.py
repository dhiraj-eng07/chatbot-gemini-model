"""
Constants used throughout the agentic chatbot application.
"""

# API Configuration
DEFAULT_GEMINI_MODEL = "gemini-pro"
MAX_TOKENS = 2048
TEMPERATURE = 0.7

# Database Constants
DEFAULT_MONGO_URI = "mongodb://localhost:27017"
DEFAULT_DATABASE_NAME = "chatbot_db"
DEFAULT_USERS_COLLECTION = "users"
DEFAULT_MESSAGES_COLLECTION = "messages"
DEFAULT_CONVERSATIONS_COLLECTION = "conversations"

# Validation Constants
MIN_QUERY_LENGTH = 1
MAX_QUERY_LENGTH = 5000
MIN_USER_ID_LENGTH = 1
MAX_USER_ID_LENGTH = 256

# Message Types
MESSAGE_TYPE_USER = "user"
MESSAGE_TYPE_ASSISTANT = "assistant"

# Logging
DEFAULT_LOG_LEVEL = "INFO"
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Timeouts
DATABASE_TIMEOUT = 5000  # milliseconds
API_TIMEOUT = 30  # seconds
