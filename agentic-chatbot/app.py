from flask import Flask, request, jsonify
from flask_cors import CORS
from agents.query_agent import QueryAgent
from config import config
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Initialize the agent
agent = QueryAgent()

@app.route('/')
def home():
    return jsonify({
        "message": "🤖 Agentic Chatbot API",
        "status": "running",
        "database": "connected" if agent.db_handler.is_connected() else "demo_mode",
        "gemini_ai": "active" if agent.gemini.is_initialized() else "basic_mode",
        "endpoints": {
            "/chat": "POST - Chat with the agent",
            "/health": "GET - Check system health",
            "/info": "GET - Get system information"
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    """Main chat endpoint"""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({"error": "Message is required"}), 400
        
        message = data['message'].strip()
        session_id = data.get('session_id', f"session_{datetime.now().timestamp()}")
        
        if not message:
            return jsonify({"error": "Message cannot be empty"}), 400
        
        logger.info(f"💬 Processing: {message}")
        
        # Process query
        result = agent.process_query(message, session_id)
        
        response = {
            "response": result["response"],
            "session_id": session_id,
            "timestamp": result["timestamp"],
            "status": result["status"],
            "system_info": {
                "database": "connected" if agent.db_handler.is_connected() else "demo_mode",
                "ai": "active" if agent.gemini.is_initialized() else "basic_mode"
            }
        }
        
        return jsonify(response)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        return jsonify({
            "response": f"Sorry, I encountered an error: {str(e)}",
            "error": True
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "database": agent.db_handler.is_connected(),
        "gemini": agent.gemini.is_initialized()
    })

@app.route('/info', methods=['GET'])
def system_info():
    """Get system information"""
    return jsonify({
        "database": {
            "connected": agent.db_handler.is_connected(),
            "name": config.DATABASE_NAME,
            "uri": config.MONGO_URI[:50] + "..." if len(config.MONGO_URI) > 50 else config.MONGO_URI,
            "stats": agent.db_handler.get_all_data_summary()
        },
        "gemini": {
            "active": agent.gemini.is_initialized(),
            "model": agent.gemini.model_name if agent.gemini.is_initialized() else "not_available"
        }
    })

@app.route('/demo', methods=['GET'])
def demo_queries():
    """Get demo queries"""
    demo_queries = [
        "How many users do we have?",
        "Show me all products",
        "What's the total sales?",
        "Find electronics products",
        "How many orders are there?",
        "Give me a summary"
    ]
    return jsonify({"demo_queries": demo_queries})

if __name__ == '__main__':
    logger.info(f"🚀 Starting Agentic Chatbot on port {config.PORT}")
    logger.info(f"📊 MongoDB: {config.MONGO_URI}")
    logger.info(f"🗃️ Database: {config.DATABASE_NAME}")
    logger.info(f"🤖 Gemini: {'Active' if agent.gemini.is_initialized() else 'Basic Mode'}")
    app.run(host='0.0.0.0', port=config.PORT, debug=config.DEBUG)