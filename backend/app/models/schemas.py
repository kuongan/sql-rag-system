from typing import Dict, Any, List, Optional, TypedDict
from pydantic import BaseModel

class QueryRequest(BaseModel):
    query: str
    conversation_id: Optional[str] = "default"
    user_id: Optional[str] = "anonymous"
    conversation_history: Optional[List[Dict[str, Any]]] = []

class QueryResponse(BaseModel):
    success: bool
    query: str
    intent: Optional[str] = None
    response: Dict[str, Any]
    agents_used: List[str]
    conversation_id: str
    user_id: str
    conversation_history: Optional[List[Dict[str, Any]]] = None
    explanation: Optional[Dict[str, Any]] = None
    error: Optional[str] = None