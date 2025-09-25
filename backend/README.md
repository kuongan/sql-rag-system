# SQL RAG System Backend

A sophisticated multi-agent system that combines SQL querying, document retrieval, and data visualization capabilities using LangGraph and ReAct patterns.

## 🏗️ Architecture

The backend is built with a modular agent-based architecture featuring:

- **ReAct Orchestrator**: Intelligent agent coordination using ReAct (Reasoning + Acting) pattern
- **Specialized Agents**: SQL, RAG, and Plotting agents with specific expertise
- **LangGraph Framework**: State management and agent workflow orchestration
- **Multi-model Support**: Google Gemini AI integration via LangChain
- **Vector Storage**: FAISS for document embeddings and semantic search
- **Database Integration**: SQLite support with automatic schema introspection
- **Load Balancing**: Multi-key API management for scalability
- **Conversation Memory**: Persistent context across interactions

## �🚀 Quick Start

### 1. Environment Setup

Create a `.env` file with your API keys:
```bash
GOOGLE_API_KEY=your_primary_key
GOOGLE_API_KEY_1=your_secondary_key
# Add more keys for load balancing
DATABASE_URL=your_url
# LangSmith Configuration (optional)
LANGSMITH_API_KEY=your_langsmith_key
LANGSMITH_PROJECT=name_project
LANGSMITH_ENDPOINT=https://api.smith.langchain.com
LANGSMITH_TRACING=true
# Vector Store Configuration
FAISS_STORE_PATH=./data/faiss_store
```

### 2. Install Dependencies

Using Poetry (recommended):
```bash
poetry install
```

Or using pip:
```bash
pip install -r requirements.txt
```
### 3. Initialize Data Stores

Process PDF documents to FAISS vector store:
```bash
python scripts/ingest_pdf_to_faiss.py
```

Migrate SQLite data to main database:
```bash
python scripts/ingest_sqlite_to_sql.py
```

## Database Schema

The system works with travel booking data containing:

- **aircrafts_data** (9 rows) - Aircraft information
- **airports_data** (104 rows) - Airport details
- **boarding_passes** (579,686 rows) - Passenger boarding data
- **bookings** (262,788 rows) - Booking records
- **flights** (33,121 rows) - Flight schedules
- **seats** (1,339 rows) - Seat configurations
- **ticket_flights** (1,045,726 rows) - Ticket-flight relationships
- **tickets** (366,733 rows) - Ticket information

## API Integration
```http
# Orchestrator endpoint (recommended)
POST /api/v1/orchestrator/query
{
  "query": "Show me flight statistics and visualize the data",
  "conversation_id": "session_123",
  "user_id": "user_456"
}

# Direct agent access
POST /api/v1/agents/sql/query
{"question": "SELECT COUNT(*) FROM flights"}

POST /api/v1/agents/rag/query  
{"question": "What are the check-in procedures?"}

POST /api/v1/agents/plotting/create
{
  "data": [...],
  "plot_request": "Create a line chart showing trends"
}
```