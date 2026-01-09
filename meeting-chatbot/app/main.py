from fastapi import FastAPI, HTTPException, UploadFile, File, Form, Depends
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional
import json
import uuid
import logging
from datetime import datetime

from app.config import settings
from app.database import db
from app.models import MeetingSummary, ChatQuery, ChatResponse, Document
from app.summary_generator import SummaryGenerator
from app.chatbot import chatbot

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Gemini Chatbot API with MongoDB",
    description="Intelligent Chatbot powered by Gemini AI that answers questions based on connected documents and data stored in MongoDB",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup and shutdown events
@app.on_event("startup")
async def startup_event():
    await db.connect()
    logger.info("Application started")

@app.on_event("shutdown")
async def shutdown_event():
    await db.disconnect()
    logger.info("Application shutdown")

# Health check endpoint
@app.get("/")
async def root():
    return {"message": "Meeting Summary Chatbot API", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "database": "connected" if db.client else "disconnected",
        "ai_providers": chatbot.ai_provider.get_available_providers()
    }

# Meeting endpoints
@app.post("/meetings/upload", response_model=dict)
async def upload_meeting(
    transcript: str = Form(..., description="Meeting transcript"),
    title: str = Form("Untitled Meeting"),
    participants: str = Form("[]"),
    duration_minutes: int = Form(60),
    ai_provider: str = Form("openai")
):
    """
    Upload meeting transcript and generate summary
    """
    try:
        # Parse participants
        try:
            participants_list = json.loads(participants)
        except:
            participants_list = []
        
        metadata = {
            "title": title,
            "participants": participants_list,
            "duration_minutes": duration_minutes,
            "date": datetime.now()
        }
        
        # Generate and store summary
        meeting_data = await SummaryGenerator.generate_and_store_summary(
            transcript=transcript,
            metadata=metadata,
            ai_provider_name=ai_provider
        )
        
        return {
            "message": "Meeting summary generated successfully",
            "meeting_id": meeting_data["meeting_id"],
            "data": meeting_data
        }
        
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/meetings/{meeting_id}", response_model=dict)
async def get_meeting(meeting_id: str):
    """
    Get meeting summary by ID
    """
    meeting = await db.get_meeting_by_id(meeting_id)
    if not meeting:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return meeting

@app.get("/meetings", response_model=List[dict])
async def list_meetings(
    limit: int = 20,
    offset: int = 0,
    tag: Optional[str] = None,
    participant: Optional[str] = None
):
    """
    List all meetings with optional filters
    """
    query = {}
    if tag:
        query["tags"] = tag
    if participant:
        query["participants"] = participant
    
    meetings = await db.search_meetings(query, limit=limit)
    return meetings

@app.put("/meetings/{meeting_id}", response_model=dict)
async def update_meeting(
    meeting_id: str,
    transcript: Optional[str] = None,
    ai_provider: str = "openai"
):
    """
    Update meeting transcript and regenerate summary
    """
    if not transcript:
        raise HTTPException(status_code=400, detail="Transcript is required for update")
    
    success = await SummaryGenerator.update_meeting_summary(
        meeting_id=meeting_id,
        transcript=transcript,
        ai_provider_name=ai_provider
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found or update failed")
    
    return {"message": "Meeting updated successfully"}

@app.delete("/meetings/{meeting_id}")
async def delete_meeting(meeting_id: str):
    """
    Delete a meeting
    """
    success = await db.delete_meeting(meeting_id)
    if not success:
        raise HTTPException(status_code=404, detail="Meeting not found")
    return {"message": "Meeting deleted successfully"}

# Chatbot endpoints
@app.post("/chat/ask", response_model=ChatResponse)
async def ask_question(query: ChatQuery):
    """
    Ask a question about meetings
    """
    try:
        response = await chatbot.ask_question(query)
        return response
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/chat/providers")
async def get_ai_providers():
    """
    Get available AI providers
    """
    providers = chatbot.ai_provider.get_available_providers()
    return {"available_providers": providers}

# Document endpoints
@app.post("/documents/upload", response_model=dict)
async def upload_document(
    title: str = Form(..., description="Document title"),
    content: str = Form(..., description="Document content"),
    category: str = Form(None, description="Document category"),
    tags: str = Form("[]", description="JSON array of tags"),
    metadata: str = Form("{}", description="JSON object of additional metadata")
):
    """
    Upload a document to the database
    """
    try:
        # Parse tags and metadata
        try:
            tags_list = json.loads(tags) if tags else []
        except:
            tags_list = []
        
        try:
            metadata_dict = json.loads(metadata) if metadata else {}
        except:
            metadata_dict = {}
        
        # Generate unique doc_id
        doc_id = f"DOC-{uuid.uuid4().hex[:8].upper()}"
        
        document_data = {
            "doc_id": doc_id,
            "title": title,
            "content": content,
            "category": category or "general",
            "tags": tags_list,
            "metadata": metadata_dict,
            "created_at": datetime.now(),
            "updated_at": datetime.now()
        }
        
        # Store in database
        doc_id_inserted = await db.insert_document(document_data)
        
        return {
            "message": "Document uploaded successfully",
            "doc_id": doc_id,
            "data": document_data
        }
        
    except Exception as e:
        logger.error(f"Document upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{doc_id}", response_model=dict)
async def get_document(doc_id: str):
    """
    Get document by ID
    """
    document = await db.get_document_by_id(doc_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    return document

@app.get("/documents", response_model=List[dict])
async def list_documents(
    limit: int = 20,
    offset: int = 0,
    category: Optional[str] = None,
    tag: Optional[str] = None
):
    """
    List all documents with optional filters
    """
    query = {}
    if category:
        query["category"] = category
    if tag:
        query["tags"] = tag
    
    if query:
        documents = await db.search_documents(query, limit=limit)
    else:
        documents = await db.get_all_documents(limit=limit, skip=offset)
    
    return documents

@app.put("/documents/{doc_id}", response_model=dict)
async def update_document(
    doc_id: str,
    title: Optional[str] = None,
    content: Optional[str] = None,
    category: Optional[str] = None,
    tags: Optional[str] = None,
    metadata: Optional[str] = None
):
    """
    Update an existing document
    """
    update_data = {}
    
    if title is not None:
        update_data["title"] = title
    if content is not None:
        update_data["content"] = content
    if category is not None:
        update_data["category"] = category
    if tags is not None:
        try:
            update_data["tags"] = json.loads(tags)
        except:
            raise HTTPException(status_code=400, detail="Invalid tags format")
    if metadata is not None:
        try:
            update_data["metadata"] = json.loads(metadata)
        except:
            raise HTTPException(status_code=400, detail="Invalid metadata format")
    
    if not update_data:
        raise HTTPException(status_code=400, detail="No update data provided")
    
    success = await db.update_document(doc_id, update_data)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found or update failed")
    
    return {"message": "Document updated successfully"}

@app.delete("/documents/{doc_id}")
async def delete_document(doc_id: str):
    """
    Delete a document
    """
    success = await db.delete_document(doc_id)
    if not success:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"message": "Document deleted successfully"}

# Search endpoints
@app.get("/search")
async def search_meetings(
    q: str,
    limit: int = 10,
    days: int = 30
):
    """
    Search meetings by keyword
    """
    # Get recent meetings
    meetings = await db.get_recent_meetings(days=days, limit=50)
    
    # Simple keyword search (can be enhanced with embeddings)
    results = []
    search_terms = q.lower().split()
    
    for meeting in meetings:
        content = f"{meeting.get('title', '')} {meeting.get('summary', '')}"
        content_lower = content.lower()
        
        # Check if all search terms appear
        if all(term in content_lower for term in search_terms):
            results.append({
                "meeting_id": meeting.get("meeting_id"),
                "title": meeting.get("title"),
                "date": meeting.get("date"),
                "summary_preview": meeting.get("summary", "")[:100] + "..." if len(meeting.get("summary", "")) > 100 else meeting.get("summary", "")
            })
    
    return {"query": q, "results": results[:limit]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)