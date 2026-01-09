import openai
import google.generativeai as genai
from typing import List, Dict, Any, Optional
from app.config import settings
import logging

logger = logging.getLogger(__name__)

class OpenAIHandler:
    def __init__(self):
        self.client = openai.OpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = settings.OPENAI_MODEL
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using OpenAI"""
        try:
            full_prompt = f"Context: {context}\n\nQuestion: {prompt}\n\nAnswer:"
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful meeting assistant. Answer questions based on the provided meeting context."},
                    {"role": "user", "content": full_prompt}
                ],
                max_tokens=settings.MAX_TOKENS,
                temperature=0.7
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise
    
    async def generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Generate meeting summary from transcript using OpenAI"""
        try:
            prompt = f"""
            Analyze this meeting transcript and provide:
            1. A concise summary
            2. Key discussion points (as bullet points)
            3. Action items with assignees and due dates
            4. Decisions made
            5. Relevant tags
            
            Transcript:
            {transcript}
            
            Format the response as a JSON object with these keys: summary, key_points, action_items, decisions, tags
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert meeting summarizer. Extract key information and structure it properly."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3,
                response_format={"type": "json_object"}
            )
            
            import json
            result = json.loads(response.choices[0].message.content)
            return result
        except Exception as e:
            logger.error(f"OpenAI summarization error: {e}")
            raise

class GeminiHandler:
    def __init__(self):
        if not settings.GEMINI_API_KEY or not settings.GEMINI_API_KEY.strip():
            raise ValueError("GEMINI_API_KEY is required but not set. Please set GEMINI_API_KEY in your .env file.")
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)
    
    async def generate_response(self, prompt: str, context: str = "") -> str:
        """Generate response using Gemini with RAG (Retrieval Augmented Generation)"""
        try:
            if not context or context.strip() == "":
                full_prompt = f"""You are a helpful assistant. Answer the following question to the best of your knowledge:

Question: {prompt}

Provide a clear and helpful answer."""
            else:
                full_prompt = f"""You are an intelligent assistant that answers questions based on provided context from connected documents and data.

CONTEXT FROM DATABASE:
{context}

QUESTION: {prompt}

INSTRUCTIONS:
1. Answer the question based SOLELY on the context provided above
2. If the context contains relevant information, use it to provide a detailed answer
3. If the context doesn't contain enough information to answer the question, say so clearly
4. Be accurate and cite specific details from the context when possible
5. If asked about something not in the context, politely state that you don't have that information in the connected data

Provide your answer:"""
            
            response = self.model.generate_content(
                full_prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.3,  # Lower temperature for more focused answers
                    top_p=0.8,
                    top_k=40,
                    max_output_tokens=2048,
                )
            )
            
            if hasattr(response, 'text'):
                return response.text.strip()
            else:
                # Handle alternative response formats
                return str(response).strip()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            # Try to get more details from the error
            if hasattr(e, 'message'):
                logger.error(f"Error message: {e.message}")
            raise
    
    async def generate_summary(self, transcript: str) -> Dict[str, Any]:
        """Generate meeting summary from transcript using Gemini"""
        try:
            prompt = f"""
            Analyze this meeting transcript and extract:
            - Summary
            - Key discussion points
            - Action items with assignees
            - Decisions made
            - Relevant tags
            
            Return the output in JSON format with these keys: summary, key_points, action_items, decisions, tags
            
            Transcript:
            {transcript}
            """
            
            response = self.model.generate_content(prompt)
            
            # Parse response (Gemini might return text that needs JSON parsing)
            import json
            import re
            
            # Try to extract JSON from response
            text = response.text
            json_match = re.search(r'\{.*\}', text, re.DOTALL)
            
            if json_match:
                result = json.loads(json_match.group())
            else:
                # Fallback: Create structured response
                result = {
                    "summary": text[:500] + "..." if len(text) > 500 else text,
                    "key_points": [],
                    "action_items": [],
                    "decisions": [],
                    "tags": []
                }
            
            return result
        except Exception as e:
            logger.error(f"Gemini summarization error: {e}")
            raise

class AIProvider:
    """Factory class to manage AI providers"""
    
    def __init__(self):
        # Initialize OpenAI handler if API key is available
        try:
            self.openai_handler = OpenAIHandler() if settings.OPENAI_API_KEY and settings.OPENAI_API_KEY.strip() else None
        except Exception as e:
            logger.warning(f"Failed to initialize OpenAI handler: {e}")
            self.openai_handler = None
        
        # Initialize Gemini handler if API key is available
        try:
            self.gemini_handler = GeminiHandler() if settings.GEMINI_API_KEY and settings.GEMINI_API_KEY.strip() else None
        except Exception as e:
            logger.warning(f"Failed to initialize Gemini handler: {e}")
            self.gemini_handler = None
        
        # Warn if no providers are available
        if not self.openai_handler and not self.gemini_handler:
            logger.error("No AI providers are available! Please set at least one API key (GEMINI_API_KEY or OPENAI_API_KEY) in your .env file.")
    
    async def get_response(self, prompt: str, context: str = "", provider: str = "openai") -> str:
        """Get response from specified AI provider"""
        if provider == "openai" and self.openai_handler:
            return await self.openai_handler.generate_response(prompt, context)
        elif provider == "gemini" and self.gemini_handler:
            return await self.gemini_handler.generate_response(prompt, context)
        else:
            raise ValueError(f"Unsupported or unavailable AI provider: {provider}")
    
    async def generate_meeting_summary(self, transcript: str, provider: str = "openai") -> Dict[str, Any]:
        """Generate meeting summary using specified provider"""
        if provider == "openai" and self.openai_handler:
            return await self.openai_handler.generate_summary(transcript)
        elif provider == "gemini" and self.gemini_handler:
            return await self.gemini_handler.generate_summary(transcript)
        else:
            raise ValueError(f"Unsupported or unavailable AI provider: {provider}")
    
    def get_available_providers(self) -> List[str]:
        """Get list of available AI providers"""
        providers = []
        if self.openai_handler:
            providers.append("openai")
        if self.gemini_handler:
            providers.append("gemini")
        return providers

# Create AI provider instance
ai_provider = AIProvider()