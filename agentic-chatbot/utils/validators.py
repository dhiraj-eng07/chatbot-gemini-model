"""
Validators for input validation and data verification.
"""

import re
from typing import Tuple


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format.
    
    Args:
        email: Email address to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if re.match(pattern, email):
        return True, "Valid email"
    return False, "Invalid email format"


def validate_query(query: str, min_length: int = 1, max_length: int = 5000) -> Tuple[bool, str]:
    """
    Validate user query.
    
    Args:
        query: Query string to validate
        min_length: Minimum length of query
        max_length: Maximum length of query
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) < min_length:
        return False, f"Query must be at least {min_length} characters"
    
    if len(query) > max_length:
        return False, f"Query cannot exceed {max_length} characters"
    
    return True, "Valid query"


def validate_user_id(user_id: str) -> Tuple[bool, str]:
    """
    Validate user ID format.
    
    Args:
        user_id: User ID to validate
    
    Returns:
        Tuple of (is_valid, message)
    """
    if not user_id or not user_id.strip():
        return False, "User ID cannot be empty"
    
    if not user_id.isalnum():
        return False, "User ID must contain only alphanumeric characters"
    
    return True, "Valid user ID"
