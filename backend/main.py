from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from contextlib import asynccontextmanager
import uvicorn
import logging
from dotenv import load_dotenv
load_dotenv()

from app.config import settings
from app.api.router import router as agents_router

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    # Startup
    logger.info("Text2SQL Multi-Agent System starting up...")
    logger.info(f"LangSmith tracking: {'enabled' if settings.LANGSMITH_API_KEY else 'disabled'}")
    yield
    # Shutdown - cleanup if needed
    logger.info("Text2SQL Multi-Agent System shutting down...")


def create_application() -> FastAPI:
    """Create and configure FastAPI application"""
    
    app = FastAPI(
        title=settings.PROJECT_NAME,
        version="1.0.0",
        description="Multi-Agent System for Text2SQL with RAG, LangGraph, LangChain, and LangSmith",
        openapi_url=f"{settings.API_STR}/openapi.json",
        lifespan=lifespan
    )

    # Add middleware
    if settings.BACKEND_CORS_ORIGINS:
        app.add_middleware(
            CORSMiddleware,
            allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    app.add_middleware(
        TrustedHostMiddleware, 
        allowed_hosts=["*"]  # Configure appropriately for production
    )

    # Include routers
    app.include_router(agents_router, prefix=settings.API_STR)  # Multi-agent router

    @app.get("/")
    async def root():
        return {
            "message": "Text2SQL Multi-Agent System",
            "version": "1.0.0",
            "description": "A sophisticated multi-agent system built with LangGraph, LangChain, and LangSmith",
            "agents": [
                "SQL Execute Agent - Convert natural language to SQL queries",
                "RAG Agent - Retrieve information from Swiss Airlines FAQ",
                "Data Plotting Agent - Create visualizations and charts",
                "Orchestrator Agent - Coordinate all agents"
            ],
            "docs": f"{settings.API_STR}/docs",
            "capabilities": f"{settings.API_STR}/agents/capabilities",
            "health": "/health"
        }

    @app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "text2sql-multiagent-backend"}

    return app


app = create_application()

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
