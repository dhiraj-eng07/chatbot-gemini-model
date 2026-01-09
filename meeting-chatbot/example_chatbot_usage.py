"""
Example script demonstrating how to use the Gemini Chatbot API with MongoDB
"""

import requests
import json

# Base URL for the API
BASE_URL = "http://localhost:8000"

def upload_document(title: str, content: str, category: str = "general", tags: list = None):
    """Upload a document to the database"""
    url = f"{BASE_URL}/documents/upload"
    
    data = {
        "title": title,
        "content": content,
        "category": category,
        "tags": json.dumps(tags or []),
        "metadata": json.dumps({})
    }
    
    response = requests.post(url, data=data)
    if response.status_code == 200:
        result = response.json()
        print(f"✓ Document uploaded: {result['doc_id']}")
        return result['doc_id']
    else:
        print(f"✗ Error uploading document: {response.text}")
        return None

def ask_question(question: str, ai_provider: str = "gemini", doc_id: str = None):
    """Ask a question to the chatbot"""
    url = f"{BASE_URL}/chat/ask"
    
    payload = {
        "question": question,
        "ai_provider": ai_provider
    }
    
    if doc_id:
        payload["doc_id"] = doc_id
    
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        result = response.json()
        print(f"\n📝 Question: {question}")
        print(f"🤖 Answer ({result['ai_provider']}): {result['answer']}")
        print(f"📊 Confidence: {result['confidence']:.2f}")
        
        if result.get('sources'):
            print(f"\n📚 Sources:")
            for i, source in enumerate(result['sources'], 1):
                print(f"  {i}. {source.get('title', 'Unknown')}")
        
        return result
    else:
        print(f"✗ Error asking question: {response.text}")
        return None

def list_documents():
    """List all documents"""
    url = f"{BASE_URL}/documents"
    response = requests.get(url)
    if response.status_code == 200:
        documents = response.json()
        print(f"\n📄 Found {len(documents)} documents:")
        for doc in documents:
            print(f"  - {doc.get('doc_id')}: {doc.get('title')} ({doc.get('category')})")
        return documents
    else:
        print(f"✗ Error listing documents: {response.text}")
        return []

def check_health():
    """Check if the API is running"""
    url = f"{BASE_URL}/health"
    try:
        response = requests.get(url)
        if response.status_code == 200:
            result = response.json()
            print(f"✓ API is healthy")
            print(f"  Database: {result.get('database')}")
            print(f"  AI Providers: {', '.join(result.get('ai_providers', []))}")
            return True
        else:
            print(f"✗ API health check failed: {response.text}")
            return False
    except requests.exceptions.ConnectionError:
        print("✗ Cannot connect to API. Make sure the server is running on http://localhost:8000")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Gemini Chatbot with MongoDB - Example Usage")
    print("=" * 60)
    
    # Check if API is running
    if not check_health():
        exit(1)
    
    print("\n" + "=" * 60)
    print("1. Uploading Sample Documents")
    print("=" * 60)
    
    # Upload sample documents
    doc1_content = """
    Project Gemini Chatbot is an intelligent chatbot system that uses Google's Gemini AI 
    to answer questions based on documents stored in MongoDB. The system implements 
    RAG (Retrieval Augmented Generation) to provide accurate answers from connected data.
    
    Key Features:
    - Uses Gemini AI for intelligent responses
    - Stores documents in MongoDB
    - Retrieves relevant context from database
    - Answers questions based on connected documents
    """
    
    doc2_content = """
    MongoDB is a NoSQL database that stores data in flexible, JSON-like documents. 
    In this chatbot system, MongoDB is used to store:
    - General documents uploaded by users
    - Meeting summaries and transcripts
    - Document metadata and tags
    
    The database is queried to find relevant documents when answering questions.
    """
    
    doc1_id = upload_document(
        title="Gemini Chatbot Project",
        content=doc1_content,
        category="documentation",
        tags=["project", "chatbot", "gemini"]
    )
    
    doc2_id = upload_document(
        title="MongoDB Database",
        content=doc2_content,
        category="database",
        tags=["mongodb", "database", "storage"]
    )
    
    print("\n" + "=" * 60)
    print("2. Listing All Documents")
    print("=" * 60)
    list_documents()
    
    print("\n" + "=" * 60)
    print("3. Asking Questions (RAG - Retrieval Augmented Generation)")
    print("=" * 60)
    
    # Ask questions that should be answered from the documents
    questions = [
        "What is the Gemini Chatbot project about?",
        "How does MongoDB work in this system?",
        "What are the key features of the chatbot?",
        "What data is stored in MongoDB?"
    ]
    
    for question in questions:
        ask_question(question, ai_provider="gemini")
        print("-" * 60)
    
    # Ask a question about a specific document
    if doc1_id:
        print("\n" + "=" * 60)
        print("4. Asking Question about Specific Document")
        print("=" * 60)
        ask_question(
            "What technologies are used in this project?",
            ai_provider="gemini",
            doc_id=doc1_id
        )
    
    print("\n" + "=" * 60)
    print("Example completed!")
    print("=" * 60)

