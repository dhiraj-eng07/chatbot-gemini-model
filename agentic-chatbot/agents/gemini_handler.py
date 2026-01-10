import google.generativeai as genai
from typing import Optional, Dict, Any
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiHandler:
    def __init__(self):
        self.api_key = config.GEMINI_API_KEY
        self.model = None
        self.model_name = None
        self.initialize()
    
    def initialize(self):
        """Initialize Gemini AI with automatic model detection"""
        try:
            if not self.api_key:
                logger.warning("⚠️ Gemini API key not provided. Running without AI.")
                return
            
            logger.info("🔧 Initializing Gemini AI...")
            genai.configure(api_key=self.api_key)
            
            # List available models
            models = genai.list_models()
            available_models = [model.name for model in models]
            logger.info(f"📋 Available models: {available_models}")
            
            # Try to find a suitable Gemini model
            gemini_models = [
                "gemini-1.5-pro",
                "gemini-1.5-flash", 
                "gemini-pro",
                "gemini-1.0-pro",
                "models/gemini-1.5-pro",
                "models/gemini-1.5-flash"
            ]
            
            for model_candidate in gemini_models:
                for available_model in available_models:
                    if model_candidate in available_model:
                        try:
                            self.model_name = available_model
                            self.model = genai.GenerativeModel(available_model)
                            logger.info(f"✅ Using Gemini model: {available_model}")
                            return
                        except Exception as e:
                            logger.warning(f"Could not initialize {available_model}: {e}")
                            continue
            
            # If no specific model found, try the first available
            if available_models:
                self.model_name = available_models[0]
                self.model = genai.GenerativeModel(available_models[0])
                logger.info(f"✅ Using available model: {available_models[0]}")
            else:
                logger.error("❌ No available models found")
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini AI: {e}")
            self.model = None
    
    def is_initialized(self):
        """Check if Gemini is initialized"""
        return self.model is not None
    
    def generate_response(self, prompt: str) -> str:
        """Generate response using Gemini AI"""
        if not self.is_initialized():
            return "I'm running in basic mode. For AI features, please add your Gemini API key to the .env file."
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return f"I encountered an error: {str(e)[:100]}"
    
    def analyze_query_simple(self, user_query: str) -> Dict[str, str]:
        """Simple query analysis without complex JSON parsing"""
        query_lower = user_query.lower()
        
        # Determine entity
        if any(word in query_lower for word in ["user", "customer", "person", "people"]):
            entity = "users"
        elif any(word in query_lower for word in ["product", "item", "goods", "item"]):
            entity = "products"
        elif any(word in query_lower for word in ["order", "sale", "purchase", "transaction"]):
            entity = "orders"
        elif any(word in query_lower for word in ["all", "everything", "summary", "overview"]):
            entity = "all"
        else:
            entity = "general"
        
        # Determine action
        if any(word in query_lower for word in ["count", "how many", "number", "total"]):
            action = "count"
        elif any(word in query_lower for word in ["show", "display", "list", "get", "find", "search"]):
            action = "list"
        elif any(word in query_lower for word in ["price", "cost", "expensive", "cheap"]):
            action = "price_query"
        else:
            action = "general"
        
        return {
            "entity": entity,
            "action": action,
            "query": user_query
        }