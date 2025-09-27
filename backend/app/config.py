from pydantic_settings import BaseSettings
from typing import List, Optional
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings(BaseSettings):
    # Application
    PROJECT_NAME: str = "Text2SQL Multi-Agent System"
    VERSION: str = "1.0.0"
    API_STR: str = "/api"
    
    # CORS
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000"
    ]
    
    # Database
    DATABASE_URL: str = "sqlite:///./data/travel.sqlite"
    
    # Vector Database
    FAISS_STORE_PATH: str = "./data/faiss_store"
    
    # API Keys
    GOOGLE_API_KEY: Optional[str] = None
    LANGSMITH_API_KEY: Optional[str] = None
    LANGSMITH_PROJECT: str = "text2sql-multiagent"
    LANGSMITH_ENDPOINT: str = "https://api.smith.langchain.com"
    
    # Agent Configuration
    LLM_MODEL: str = "gemini-2.5-flash-lite"
    EMBEDDING_MODEL: str = "models/embedding-001"
    
    # Rate Limiting
    MAX_REQUESTS_PER_MINUTE: int = 30
    
    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from .env


# Create global settings instance
settings = Settings()