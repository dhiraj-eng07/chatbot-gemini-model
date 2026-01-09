from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from bson import ObjectId
from pymongo import IndexModel, ASCENDING

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate
    
    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)
    
    @classmethod
    def __modify_schema__(cls, field_schema):
        field_schema.update(type="string")

class MeetingSummary(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    meeting_id: str = Field(..., description="Unique identifier for the meeting")
    title: str = Field(..., description="Meeting title")
    participants: List[str] = Field(default=[], description="List of participants")
    date: datetime = Field(default_factory=datetime.now, description="Meeting date")
    duration_minutes: int = Field(..., description="Meeting duration in minutes")
    transcript: str = Field(..., description="Full meeting transcript")
    summary: str = Field(..., description="AI-generated summary")
    key_points: List[str] = Field(default=[], description="Key discussion points")
    action_items: List[Dict[str, Any]] = Field(default=[], description="Action items with assignees")
    decisions: List[str] = Field(default=[], description="Decisions made")
    tags: List[str] = Field(default=[], description="Tags for categorization")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "meeting_id": "MTG-2023-001",
                "title": "Project Kickoff",
                "participants": ["john@example.com", "jane@example.com"],
                "duration_minutes": 60,
                "summary": "Project kickoff meeting discussing scope and timelines...",
                "key_points": ["Scope finalization", "Timeline approval"],
                "action_items": [{"task": "Prepare requirements", "assignee": "john", "due_date": "2023-12-31"}]
            }
        }

class ChatQuery(BaseModel):
    question: str = Field(..., description="User's question")
    meeting_id: Optional[str] = Field(None, description="Specific meeting ID to query (optional)")
    doc_id: Optional[str] = Field(None, description="Specific document ID to query (optional)")
    ai_provider: str = Field("gemini", description="AI provider to use (openai or gemini)")
    context_days: Optional[int] = Field(30, description="Number of days to look back for context")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="AI-generated answer")
    sources: List[Dict[str, Any]] = Field(default=[], description="Source documents/meetings information")
    ai_provider: str = Field(..., description="AI provider used")
    confidence: float = Field(..., description="Confidence score of the answer")

class Document(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    doc_id: str = Field(..., description="Unique identifier for the document")
    title: str = Field(..., description="Document title")
    content: str = Field(..., description="Document content")
    category: Optional[str] = Field(None, description="Document category")
    tags: List[str] = Field(default=[], description="Tags for categorization")
    metadata: Optional[Dict[str, Any]] = Field(default={}, description="Additional metadata")
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)
    
    class Config:
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
        schema_extra = {
            "example": {
                "doc_id": "DOC-001",
                "title": "Project Documentation",
                "content": "This document contains project information...",
                "category": "documentation",
                "tags": ["project", "documentation"],
                "metadata": {"author": "John Doe", "version": "1.0"}
            }
        }