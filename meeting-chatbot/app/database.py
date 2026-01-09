from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import IndexModel, ASCENDING, DESCENDING, TEXT
from app.config import settings
from app.models import MeetingSummary
import logging

logger = logging.getLogger(__name__)

class Database:
    client: AsyncIOMotorClient = None
    database = None
    meeting_summaries = None
    documents = None
    
    async def connect(self):
        """Connect to MongoDB"""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL)
            self.database = self.client[settings.MONGODB_DATABASE]
            self.meeting_summaries = self.database.meeting_summaries
            self.documents = self.database.documents  # General documents collection
            
            # Create indexes
            await self.create_indexes()
            logger.info("Connected to MongoDB successfully")
            
        except Exception as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
    
    async def disconnect(self):
        """Disconnect from MongoDB"""
        if self.client:
            self.client.close()
            logger.info("Disconnected from MongoDB")
    
    async def create_indexes(self):
        """Create necessary indexes"""
        # Indexes for meeting summaries
        meeting_indexes = [
            IndexModel([("meeting_id", ASCENDING)], unique=True),
            IndexModel([("title", TEXT)]),
            IndexModel([("date", DESCENDING)]),
            IndexModel([("tags", ASCENDING)]),
            IndexModel([("participants", ASCENDING)]),
        ]
        await self.meeting_summaries.create_indexes(meeting_indexes)
        
        # Indexes for general documents
        document_indexes = [
            IndexModel([("doc_id", ASCENDING)], unique=True),
            IndexModel([("title", TEXT), ("content", TEXT)]),
            IndexModel([("category", ASCENDING)]),
            IndexModel([("tags", ASCENDING)]),
            IndexModel([("created_at", DESCENDING)]),
        ]
        await self.documents.create_indexes(document_indexes)
    
    async def insert_meeting_summary(self, meeting_data: dict) -> str:
        """Insert a new meeting summary"""
        try:
            result = await self.meeting_summaries.insert_one(meeting_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting meeting summary: {e}")
            raise
    
    async def get_meeting_by_id(self, meeting_id: str) -> dict:
        """Get meeting summary by meeting_id"""
        try:
            meeting = await self.meeting_summaries.find_one({"meeting_id": meeting_id})
            return meeting
        except Exception as e:
            logger.error(f"Error fetching meeting: {e}")
            return None
    
    async def search_meetings(self, query: dict, limit: int = 10) -> list:
        """Search for meetings based on query"""
        try:
            cursor = self.meeting_summaries.find(query).limit(limit)
            meetings = await cursor.to_list(length=limit)
            return meetings
        except Exception as e:
            logger.error(f"Error searching meetings: {e}")
            return []
    
    async def get_recent_meetings(self, days: int = 7, limit: int = 20) -> list:
        """Get recent meetings from the last N days"""
        from datetime import datetime, timedelta
        
        try:
            cutoff_date = datetime.now() - timedelta(days=days)
            query = {"date": {"$gte": cutoff_date}}
            
            cursor = self.meeting_summaries.find(query).sort("date", DESCENDING).limit(limit)
            meetings = await cursor.to_list(length=limit)
            return meetings
        except Exception as e:
            logger.error(f"Error fetching recent meetings: {e}")
            return []
    
    async def update_meeting_summary(self, meeting_id: str, update_data: dict) -> bool:
        """Update an existing meeting summary"""
        try:
            update_data["updated_at"] = datetime.now()
            result = await self.meeting_summaries.update_one(
                {"meeting_id": meeting_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating meeting: {e}")
            return False
    
    async def delete_meeting(self, meeting_id: str) -> bool:
        """Delete a meeting summary"""
        try:
            result = await self.meeting_summaries.delete_one({"meeting_id": meeting_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting meeting: {e}")
            return False
    
    # General document methods
    async def insert_document(self, document_data: dict) -> str:
        """Insert a general document"""
        try:
            result = await self.documents.insert_one(document_data)
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error inserting document: {e}")
            raise
    
    async def get_document_by_id(self, doc_id: str) -> dict:
        """Get document by doc_id"""
        try:
            document = await self.documents.find_one({"doc_id": doc_id})
            return document
        except Exception as e:
            logger.error(f"Error fetching document: {e}")
            return None
    
    async def search_documents(self, query: dict, limit: int = 20) -> list:
        """Search documents based on query"""
        try:
            cursor = self.documents.find(query).limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error searching documents: {e}")
            return []
    
    async def search_documents_text(self, search_text: str, limit: int = 10) -> list:
        """Search documents by text content (simple keyword search)"""
        try:
            query = {
                "$or": [
                    {"title": {"$regex": search_text, "$options": "i"}},
                    {"content": {"$regex": search_text, "$options": "i"}},
                    {"tags": {"$in": [search_text.lower()]}}
                ]
            }
            cursor = self.documents.find(query).limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error searching documents by text: {e}")
            return []
    
    async def get_all_documents(self, limit: int = 50, skip: int = 0) -> list:
        """Get all documents"""
        try:
            cursor = self.documents.find().sort("created_at", DESCENDING).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            return documents
        except Exception as e:
            logger.error(f"Error fetching documents: {e}")
            return []
    
    async def update_document(self, doc_id: str, update_data: dict) -> bool:
        """Update an existing document"""
        try:
            from datetime import datetime
            update_data["updated_at"] = datetime.now()
            result = await self.documents.update_one(
                {"doc_id": doc_id},
                {"$set": update_data}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating document: {e}")
            return False
    
    async def delete_document(self, doc_id: str) -> bool:
        """Delete a document"""
        try:
            result = await self.documents.delete_one({"doc_id": doc_id})
            return result.deleted_count > 0
        except Exception as e:
            logger.error(f"Error deleting document: {e}")
            return False

# Create database instance
db = Database()