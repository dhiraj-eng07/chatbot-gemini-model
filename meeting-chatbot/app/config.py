import os
from typing import Literal
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # MongoDB Configuration
    MONGODB_URL: str = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
    MONGODB_DATABASE: str = os.getenv("MONGODB_DATABASE", "chatbot_db")
    
    # Document/Context Configuration
    MAX_CONTEXT_DOCUMENTS: int = int(os.getenv("MAX_CONTEXT_DOCUMENTS", 10))
    CHUNK_SIZE: int = int(os.getenv("CHUNK_SIZE", 1000))
    CHUNK_OVERLAP: int = int(os.getenv("CHUNK_OVERLAP", 200))
    
    # OpenAI Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
    
    # Gemini Configuration
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Application Configuration
    DEFAULT_AI_PROVIDER: Literal["openai", "gemini"] = os.getenv("DEFAULT_AI_PROVIDER", "gemini")
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", 1000))
    
    class Config:
        env_file = ".env"

settings = Settings()