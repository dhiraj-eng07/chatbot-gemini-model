# Quick Start Guide

## Prerequisites

1. **Python 3.8+** installed on your system
2. **MongoDB** running locally or accessible MongoDB instance
3. **Gemini API Key** from [Google AI Studio](https://makersuite.google.com/app/apikey)

## Setup Steps

### 1. Install Dependencies

```bash
cd meeting-chatbot
pip install -r requirements.txt
```

### 2. Configure Environment Variables

Create a `.env` file in the `meeting-chatbot` directory:

```env
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=chatbot_db
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash
DEFAULT_AI_PROVIDER=gemini
```

### 3. Start MongoDB (if running locally)

**Windows:**
```bash
# If MongoDB is installed as a service, it should already be running
# Otherwise, start it manually:
mongod
```

**Linux/Mac:**
```bash
# Using systemd
sudo systemctl start mongod

# Or manually
mongod --dbpath /path/to/data/directory
```

### 4. Start the API Server

```bash
python -m app.main
```

Or with uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### 5. Verify Installation

Open your browser and visit:
- Health check: `http://localhost:8000/health`
- API Docs: `http://localhost:8000/docs`

## Basic Usage

### Using Python Script

Run the example script:
```bash
python example_chatbot_usage.py
```

### Using cURL

#### Upload a Document
```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "title=Project Documentation" \
  -F "content=This is my project documentation..." \
  -F "category=documentation" \
  -F "tags=[\"project\", \"docs\"]"
```

#### Ask a Question
```bash
curl -X POST "http://localhost:8000/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this project about?",
    "ai_provider": "gemini"
  }'
```

#### List Documents
```bash
curl "http://localhost:8000/documents"
```

## How It Works

1. **Upload Documents**: Store your documents/data in MongoDB using the `/documents/upload` endpoint
2. **Ask Questions**: When you ask a question via `/chat/ask`, the system:
   - Searches MongoDB for relevant documents
   - Retrieves the most relevant context
   - Sends the question + context to Gemini AI
   - Returns an answer based on your connected data
3. **RAG Process**: This is Retrieval Augmented Generation - the chatbot answers based on YOUR data, not just general knowledge

## Troubleshooting

### "GEMINI_API_KEY is required but not set"
- Make sure you created a `.env` file
- Verify the API key is correct in the `.env` file
- Restart the server after changing `.env`

### "Cannot connect to MongoDB"
- Verify MongoDB is running: `mongosh` or check the service
- Check the `MONGODB_URL` in your `.env` file
- Make sure MongoDB is accessible from your network

### "No AI providers are available"
- Check that at least one API key (GEMINI_API_KEY or OPENAI_API_KEY) is set
- Verify the API keys are valid

## Next Steps

- Upload more documents to build your knowledge base
- Experiment with different questions
- Check the API documentation at `/docs` for more endpoints
- Customize the prompts in `app/ai_handlers.py` for your use case

