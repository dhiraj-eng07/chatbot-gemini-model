"""
Exception classes for the agentic chatbot application.
"""


class ChatbotException(Exception):
    """Base exception for the chatbot application."""
    pass


class ConfigurationError(ChatbotException):
    """Raised when configuration is invalid."""
    pass


class DatabaseError(ChatbotException):
    """Raised when database operations fail."""
    pass


class ValidationError(ChatbotException):
    """Raised when input validation fails."""
    pass


class GeminiAPIError(ChatbotException):
    """Raised when Gemini API calls fail."""
    pass


class QueryProcessingError(ChatbotException):
    """Raised when query processing fails."""
    pass
