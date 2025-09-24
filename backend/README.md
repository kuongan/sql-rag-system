# SQL RAG System Backend

## 🏗️ Architecture

The backend is built with a modular architecture featuring:

- **Agent-based System**: LangGraph agents for different data processing tasks
- **Multi-model Support**: Integration with Google Gemini AI via LangChain
- **Vector Storage**: FAISS for document embeddings and similarity search
- **Database Integration**: SQLite support with schema introspection
- **Load Balancing**: Multi-key API management for scalability

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

### 3. Initialize Data

Process PDF documents to FAISS:
```bash
python scripts/ingest_pdf_to_faiss.py
```

Migrate SQLite data:
```bash
python scripts/ingest_sqlite_to_sql.py
```

## 🤖 Agents System

### Base Agent (`app/agents/base_agent.py`)
Abstract base class providing:
- LLM initialization with multi-key support
- State management with LangGraph
- Tool integration framework
- Error handling and logging

### SQL Agent
Specialized agent for database operations:
- Natural language to SQL conversion
- Database schema introspection
- Query execution and result formatting
- Error handling for malformed queries

## 📊 Database Schema

The system works with travel booking data containing:

- **aircrafts_data** (9 rows) - Aircraft information
- **airports_data** (104 rows) - Airport details
- **boarding_passes** (579,686 rows) - Passenger boarding data
- **bookings** (262,788 rows) - Booking records
- **flights** (33,121 rows) - Flight schedules
- **seats** (1,339 rows) - Seat configurations
- **ticket_flights** (1,045,726 rows) - Ticket-flight relationships
- **tickets** (366,733 rows) - Ticket information

## 🔧 Key Components

### API Key Management (`app/utils/manager.py`)
- Multi-key rotation for rate limit management
- Automatic failover between API keys
- Load balancing strategies (round-robin, random)

### Database Utilities (`app/utils/database.py`)
- SQLite connection management
- Schema introspection
- Query execution with error handling
- Result formatting and validation

### Data Models (`app/models/agents/`)
- Type-safe state management
- Pydantic models for validation
- Extensible agent result structures

## 🛠️ Scripts

### PDF Ingestion (`scripts/ingest_pdf_to_faiss.py`)
- Extracts text from PDF documents
- Semantic chunking with overlap
- Embedding generation using Google GenAI
- FAISS index creation and persistence

### SQLite Migration (`scripts/ingest_sqlite_to_sql.py`)
- Automated table structure detection
- Data type mapping and conversion
- Batch processing for large datasets
- Target database table creation
