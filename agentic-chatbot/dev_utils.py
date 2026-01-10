"""
Development and testing utilities for the agentic chatbot.
"""

from typing import Dict, List


class MockGeminiResponse:
    """Mock Gemini API response for testing."""
    
    def __init__(self, text: str):
        self.text = text


class TestDataGenerator:
    """Generate test data for development and testing."""
    
    @staticmethod
    def generate_test_user() -> Dict:
        """Generate a test user."""
        return {
            "user_id": "test_user_001",
            "name": "Test User",
            "email": "test@example.com"
        }
    
    @staticmethod
    def generate_test_messages() -> List[Dict]:
        """Generate test messages."""
        return [
            {
                "role": "user",
                "content": "What is machine learning?"
            },
            {
                "role": "assistant",
                "content": "Machine learning is a subset of artificial intelligence..."
            },
            {
                "role": "user",
                "content": "Can you give me examples?"
            }
        ]
    
    @staticmethod
    def generate_test_conversation() -> Dict:
        """Generate a test conversation."""
        return {
            "conversation_id": "conv_001",
            "user_id": "test_user_001",
            "messages": TestDataGenerator.generate_test_messages()
        }


def print_startup_banner():
    """Print application startup banner."""
    banner = """
    ╔════════════════════════════════════════╗
    ║     Agentic Chatbot - Powered by       ║
    ║      Google Gemini & MongoDB           ║
    ║          Version 1.0.0                 ║
    ╚════════════════════════════════════════╝
    """
    print(banner)
