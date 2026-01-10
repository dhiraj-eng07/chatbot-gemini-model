from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, PyMongoError
from datetime import datetime
from typing import Optional, List, Dict, Any
from config import config
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MongoDBHandler:
    def __init__(self):
        self.client = None
        self.db = None
        self.connect()
        self.ensure_collections()
    
    def connect(self):
        """Establish connection to MongoDB"""
        try:
            logger.info(f"Connecting to MongoDB...")
            logger.info(f"URI: {config.MONGO_URI[:30]}...")  # Show only first 30 chars for security
            
            self.client = MongoClient(config.MONGO_URI, serverSelectionTimeoutMS=5000)
            
            # Test the connection
            self.client.admin.command('ping')
            
            self.db = self.client[config.DATABASE_NAME]
            logger.info(f"✅ Successfully connected to MongoDB")
            logger.info(f"📊 Database: {config.DATABASE_NAME}")
            
            # List collections
            collections = self.db.list_collection_names()
            logger.info(f"📁 Collections: {collections}")
            
        except ConnectionFailure as e:
            logger.error(f"❌ Failed to connect to MongoDB: {e}")
            logger.info("⚠️ Running in demo mode without database")
            self.client = None
            self.db = None
        except Exception as e:
            logger.error(f"❌ Unexpected error: {e}")
            self.client = None
            self.db = None
    
    def ensure_collections(self):
        """Ensure all required collections exist"""
        if not self.is_connected():
            return
            
        collections = self.db.list_collection_names()
        required_collections = [
            config.USER_COLLECTION,
            config.PRODUCT_COLLECTION,
            config.ORDERS_COLLECTION,
            config.CONVERSATIONS_COLLECTION
        ]
        
        for collection in required_collections:
            if collection not in collections:
                logger.info(f"Creating collection: {collection}")
                self.db.create_collection(collection)
    
    def is_connected(self):
        """Check if MongoDB is connected - FIXED VERSION"""
        return self.client is not None
    
    # User operations
    def get_user_count(self) -> int:
        if not self.is_connected():
            return 25  # Demo data
        try:
            return self.db[config.USER_COLLECTION].count_documents({})
        except:
            return 0
    
    def get_users(self, limit: int = 10) -> List[Dict]:
        if not self.is_connected():
            # Return demo data
            return [
                {"id": "1", "name": "John Doe", "email": "john@example.com", "age": 30},
                {"id": "2", "name": "Jane Smith", "email": "jane@example.com", "age": 25}
            ]
        try:
            return list(self.db[config.USER_COLLECTION].find().limit(limit))
        except:
            return []
    
    # Product operations
    def get_product_count(self) -> int:
        if not self.is_connected():
            return 50  # Demo data
        try:
            return self.db[config.PRODUCT_COLLECTION].count_documents({})
        except:
            return 0
    
    def get_products(self, limit: int = 10) -> List[Dict]:
        if not self.is_connected():
            # Return demo data
            return [
                {"id": "1", "name": "Laptop", "price": 999.99, "category": "Electronics"},
                {"id": "2", "name": "T-shirt", "price": 19.99, "category": "Clothing"}
            ]
        try:
            return list(self.db[config.PRODUCT_COLLECTION].find().limit(limit))
        except:
            return []
    
    def search_products(self, keyword: str) -> List[Dict]:
        if not self.is_connected():
            # Demo search
            return [
                {"id": "1", "name": "Laptop", "price": 999.99, "category": "Electronics"}
            ]
        try:
            query = {
                "$or": [
                    {"name": {"$regex": keyword, "$options": "i"}},
                    {"description": {"$regex": keyword, "$options": "i"}},
                    {"category": {"$regex": keyword, "$options": "i"}}
                ]
            }
            return list(self.db[config.PRODUCT_COLLECTION].find(query).limit(10))
        except:
            return []
    
    # Order operations
    def get_total_sales(self) -> float:
        if not self.is_connected():
            return 12500.50  # Demo data
        try:
            pipeline = [
                {"$group": {"_id": None, "total": {"$sum": "$total_amount"}}}
            ]
            result = list(self.db[config.ORDERS_COLLECTION].aggregate(pipeline))
            return result[0]['total'] if result else 0
        except:
            return 0
    
    def get_orders(self, limit: int = 10) -> List[Dict]:
        if not self.is_connected():
            # Return demo data
            return [
                {"id": "1", "user_id": "1", "total_amount": 999.99, "status": "completed"},
                {"id": "2", "user_id": "2", "total_amount": 39.98, "status": "pending"}
            ]
        try:
            return list(self.db[config.ORDERS_COLLECTION].find().limit(limit))
        except:
            return []
    
    # Conversation logging
    def save_conversation(self, session_id: str, user_query: str, 
                         agent_response: str, metadata: Optional[Dict] = None) -> str:
        if not self.is_connected():
            return "demo_id"
        try:
            conversation_data = {
                "session_id": session_id,
                "user_query": user_query,
                "agent_response": agent_response,
                "metadata": metadata or {},
                "created_at": datetime.now()
            }
            result = self.db[config.CONVERSATIONS_COLLECTION].insert_one(conversation_data)
            return str(result.inserted_id)
        except:
            return "error_id"
    
    def get_all_data_summary(self) -> Dict:
        """Get summary of all data"""
        return {
            "users": self.get_user_count(),
            "products": self.get_product_count(),
            "total_sales": self.get_total_sales(),
            "connected": self.is_connected()
        }