# Agentic Chatbot

A Python-based chatbot application that leverages Google's Gemini AI and MongoDB for intelligent conversational interactions.

## Features

- **AI-Powered Responses**: Uses Google Gemini API for intelligent query processing
- **MongoDB Integration**: Persistent storage of conversations and user data
- **Query Agent**: Processes user queries with context awareness
- **Input Validation**: Comprehensive validators for email, queries, and user data
- **Modular Architecture**: Clean separation of concerns with agents, database, and utilities modules

## Project Structure

```
agentic-chatbot/
├── app.py                 # Main application entry point
├── config.py              # Configuration settings
├── database/              # Database operations module
│   ├── __init__.py
│   ├── mongodb_handler.py # MongoDB connection handler
│   └── models.py          # Data models (User, Message, Conversation)
├── agents/                # AI agents module
│   ├── __init__.py
│   ├── query_agent.py    # Query processing agent
│   └── gemini_handler.py # Gemini API integration
├── utils/                 # Utilities module
│   ├── __init__.py
│   └── validators.py     # Input validators
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
└── README.md             # This file
```

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd agentic-chatbot
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables:
```bash
cp .env.example .env
# Edit .env with your API keys and database configuration
```

## Configuration

Edit `.env` file with the following variables:

- `MONGODB_URI`: MongoDB connection string (default: mongodb://localhost:27017)
- `DATABASE_NAME`: Database name (default: chatbot_db)
- `GEMINI_API_KEY`: Your Google Gemini API key
- `DEBUG`: Debug mode (False/True)
- `LOG_LEVEL`: Logging level (INFO, DEBUG, etc.)

## Usage

```python
from agents import QueryAgent

# Initialize the query agent
agent = QueryAgent()

# Process a single query
response = agent.process_query("What is the capital of France?")
print(response)

# Handle conversation with history
messages = [
    {"role": "user", "content": "What is Python?"},
    {"role": "assistant", "content": "Python is a programming language..."},
    {"role": "user", "content": "What can I use it for?"}
]
response = agent.handle_conversation(messages)
print(response)
```

## API Endpoints

(To be added when integrating with Flask/FastAPI)

## Database Models

### User
- user_id: Unique identifier
- name: User name
- email: User email
- created_at: Creation timestamp

### Message
- user_id: Reference to user
- content: Message content
- message_type: "user" or "assistant"
- timestamp: Message timestamp

### Conversation
- conversation_id: Unique identifier
- user_id: Reference to user
- messages: List of messages
- created_at: Creation timestamp

## Validators

- `validate_email()`: Validates email format
- `validate_query()`: Validates query length and content
- `validate_user_id()`: Validates user ID format

## Dependencies

- python-dotenv: Environment variable management
- pymongo: MongoDB driver
- google-generativeai: Google Gemini API
- flask: Web framework
- requests: HTTP library

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Push to the branch
5. Create a Pull Request

## License

MIT

## Support

For issues and questions, please create an issue in the repository.
