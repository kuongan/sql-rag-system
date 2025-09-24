"""
RAG Agent Models - State and result structures for RAG Agent
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

from .base import BaseAgentState, BaseAgentResult

class RAGAgentState(BaseAgentState):
    """State for RAG Agent extending base state"""
    retrieved_documents: Optional[List[Dict[str, Any]]]
    document_sources: Optional[List[str]]
    answer: Optional[str]
    confidence_score: Optional[float]
    search_query: Optional[str]

class RAGAgentResult(BaseAgentResult):
    """Result structure for RAG Agent"""
    def __init__(self, success: bool, answer: Optional[str] = None,
                 sources: Optional[List[str]] = None,
                 retrieved_docs: Optional[List[Dict[str, Any]]] = None,
                 confidence: Optional[float] = None,
                 error: Optional[str] = None):
        super().__init__(success, error)
        self.answer = answer or ""
        self.sources = sources or []
        self.retrieved_docs = retrieved_docs or []
        self.confidence = confidence
        self.agent_type = "rag"

class DocumentSearchInput(BaseModel):
    """Input schema for document search"""
    query: str = Field(description="Search query for document retrieval")
    num_results: int = Field(default=3, description="Number of documents to retrieve (1-10)")

class RAGQueryInput(BaseModel):
    """Input schema for RAG Q&A"""
    question: str = Field(description="Question to answer using document knowledge base")