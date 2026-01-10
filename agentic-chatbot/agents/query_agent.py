from typing import Dict, Any
from datetime import datetime
from database.mongodb_handler import MongoDBHandler
from agents.gemini_handler import GeminiHandler
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class QueryAgent:
    def __init__(self):
        self.db_handler = MongoDBHandler()
        self.gemini = GeminiHandler()
        logger.info(f"📊 Database connected: {self.db_handler.is_connected()}")
        logger.info(f"🤖 Gemini AI initialized: {self.gemini.is_initialized()}")
    
    def process_query(self, user_query: str, session_id: str = "default") -> Dict[str, Any]:
        """Process user query and return response"""
        try:
            # Simple analysis
            analysis = self.gemini.analyze_query_simple(user_query)
            logger.info(f"Analysis: {analysis}")
            
            # Get data based on analysis
            data = self._get_data(analysis)
            
            # Generate response
            response = self._generate_response(user_query, data, analysis)
            
            # Save conversation
            self.db_handler.save_conversation(session_id, user_query, response, analysis)
            
            return {
                "response": response,
                "data": data,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat(),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"Error: {e}")
            return {
                "response": f"Sorry, I encountered an error: {str(e)}",
                "data": None,
                "timestamp": datetime.now().isoformat(),
                "status": "error"
            }
    
    def _get_data(self, analysis: Dict[str, str]) -> Dict:
        """Get data based on analysis"""
        entity = analysis.get("entity", "general")
        action = analysis.get("action", "general")
        
        if entity == "users":
            if action == "count":
                return {"count": self.db_handler.get_user_count(), "type": "users"}
            else:
                return {"users": self.db_handler.get_users(), "count": self.db_handler.get_user_count()}
        
        elif entity == "products":
            if action == "count":
                return {"count": self.db_handler.get_product_count(), "type": "products"}
            else:
                # Check if it's a search
                query = analysis.get("query", "").lower()
                if "search" in query or "find" in query:
                    # Extract search term (simple approach)
                    words = query.split()
                    for word in words:
                        if word not in ["find", "search", "for", "me", "show", "all"]:
                            products = self.db_handler.search_products(word)
                            return {"products": products, "count": len(products), "searched_for": word}
                
                return {"products": self.db_handler.get_products(), "count": self.db_handler.get_product_count()}
        
        elif entity == "orders":
            if action == "count":
                return {
                    "count": len(self.db_handler.get_orders()),
                    "total_sales": self.db_handler.get_total_sales(),
                    "type": "orders"
                }
            else:
                orders = self.db_handler.get_orders()
                return {"orders": orders, "count": len(orders), "total_sales": self.db_handler.get_total_sales()}
        
        elif entity == "all":
            return self.db_handler.get_all_data_summary()
        
        else:
            # General query - return summary
            return self.db_handler.get_all_data_summary()
    
    def _generate_response(self, user_query: str, data: Dict, analysis: Dict) -> str:
        """Generate response based on data"""
        
        # If Gemini is available, use it for better responses
        if self.gemini.is_initialized():
            prompt = f"""
            User asked: "{user_query}"
            
            Data from database: {data}
            
            Please provide a helpful, friendly response based on this data.
            If showing counts, mention the numbers clearly.
            If showing lists, summarize what's available.
            Keep it conversational and helpful.
            
            Response:
            """
            return self.gemini.generate_response(prompt)
        
        # Fallback simple responses
        entity = analysis.get("entity", "general")
        action = analysis.get("action", "general")
        
        if entity == "users" and action == "count":
            count = data.get("count", 0)
            return f"We have {count} users in the database."
        
        elif entity == "users":
            users = data.get("users", [])
            count = len(users)
            if count > 0:
                names = ", ".join([user.get("name", "Unknown") for user in users[:3]])
                more = " and more..." if count > 3 else ""
                return f"Found {count} users. Some of them are: {names}{more}"
            else:
                return "No users found in the database."
        
        elif entity == "products" and action == "count":
            count = data.get("count", 0)
            return f"We have {count} products available."
        
        elif entity == "products":
            products = data.get("products", [])
            count = len(products)
            if count > 0:
                if "searched_for" in data:
                    search_term = data["searched_for"]
                    return f"Found {count} products matching '{search_term}'."
                else:
                    return f"We have {count} products in various categories."
            else:
                return "No products found."
        
        elif entity == "orders":
            count = data.get("count", 0)
            total_sales = data.get("total_sales", 0)
            return f"We have {count} orders with total sales of ${total_sales:,.2f}."
        
        else:
            # General response
            summary = self.db_handler.get_all_data_summary()
            return f"Here's what I found: {summary['users']} users, {summary['products']} products, and total sales of ${summary['total_sales']:,.2f}."
    
    def chat(self, message: str) -> str:
        """Simple chat interface"""
        result = self.process_query(message)
        return result["response"]