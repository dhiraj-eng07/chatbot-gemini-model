from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class Product(BaseModel):
    id: str
    name: str
    category: str
    price: float
    stock: int
    description: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class User(BaseModel):
    id: str
    name: str
    email: str
    age: Optional[int] = None
    address: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)

class Order(BaseModel):
    id: str
    user_id: str
    products: List[Dict[str, Any]]
    total_amount: float
    status: str = "pending"
    created_at: datetime = Field(default_factory=datetime.now)

class Conversation(BaseModel):
    id: str
    session_id: str
    user_query: str
    agent_response: str
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.now)