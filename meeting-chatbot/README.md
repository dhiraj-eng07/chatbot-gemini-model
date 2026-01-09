# Gemini Chatbot with MongoDB

An intelligent chatbot application powered by Google's Gemini AI that answers questions based on documents and data stored in MongoDB. This chatbot uses RAG (Retrieval Augmented Generation) to provide accurate answers from your connected database.

## Features

- **Gemini AI Integration**: Uses Google Gemini for intelligent question answering
- **MongoDB Integration**: Stores and retrieves documents/data from MongoDB
- **RAG (Retrieval Augmented Generation)**: Answers questions based on connected documents
- **Document Management**: Upload, update, delete, and search documents
- **Meeting Summaries**: Still supports meeting transcript summarization
- **Multi-source Context**: Searches both general documents and meeting summaries
- **Flexible AI Providers**: Supports both Gemini (default) and OpenAI

## Project Structure

```
meeting-chatbot/
├── app/
│   ├── __init__.py
│   ├── main.py              # Entry point
│   ├── models.py            # Data models
│   ├── database.py          # Database operations
│   ├── ai_handlers.py       # AI processing
│   ├── summary_generator.py # Summary generation
│   ├── chatbot.py           # Main chatbot logic
│   └── config.py            # Configuration
├── requirements.txt         # Python dependencies
├── .env.example            # Environment variables template
└── README.md               # This file
```

## Installation

1. Clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create `.env` file from `.env.example`:
   ```bash
   cp .env.example .env
   ```

5. Add your API keys to the `.env` file

## Configuration

Create a `.env` file in the `meeting-chatbot` directory with the following configuration:

```env
# MongoDB Configuration (Required)
MONGODB_URL=mongodb://localhost:27017
MONGODB_DATABASE=chatbot_db

# Gemini API Configuration (Required)
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=gemini-1.5-flash

# OpenAI Configuration (Optional - if you want to use OpenAI as well)
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo

# Application Configuration
DEFAULT_AI_PROVIDER=gemini
MAX_TOKENS=2048

# Document/Context Configuration
MAX_CONTEXT_DOCUMENTS=10
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the API key and add it to your `.env` file

## Usage

### Start the Application

```bash
cd meeting-chatbot
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### API Documentation

Once the server is running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

### Example Usage

#### 1. Upload a Document

```bash
curl -X POST "http://localhost:8000/documents/upload" \
  -F "title=Project Documentation" \
  -F "content=This project involves building a chatbot system..." \
  -F "category=documentation" \
  -F "tags=[\"project\", \"chatbot\"]"
```

#### 2. Ask a Question

```bash
curl -X POST "http://localhost:8000/chat/ask" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "What is this project about?",
    "ai_provider": "gemini"
  }'
```

#### 3. List All Documents

```bash
curl "http://localhost:8000/documents"
```

## API Endpoints

### Document Endpoints
- `POST /documents/upload` - Upload a new document
- `GET /documents` - List all documents (with filters)
- `GET /documents/{doc_id}` - Get a specific document
- `PUT /documents/{doc_id}` - Update a document
- `DELETE /documents/{doc_id}` - Delete a document

### Chat Endpoints
- `POST /chat/ask` - Ask a question (uses RAG with connected documents)
- `GET /chat/providers` - Get available AI providers

### Meeting Endpoints (Still Available)
- `POST /meetings/upload` - Upload meeting transcript
- `GET /meetings` - List all meetings
- `GET /meetings/{meeting_id}` - Get a specific meeting
- `PUT /meetings/{meeting_id}` - Update a meeting
- `DELETE /meetings/{meeting_id}` - Delete a meeting

### Search Endpoint
- `GET /search?q=keyword` - Search documents and meetings by keyword

## Requirements

- Python 3.8+
- See `requirements.txt` for dependencies

## License

MIT License

## Support

For issues and questions, please open an issue in the repository.
