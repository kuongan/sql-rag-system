"""
SQL Agent Models - State and result structures for SQL Agent
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
from .base import BaseAgentState, BaseAgentResult

class SQLQueryInput(BaseModel):
    """Input schema for SQL query tool"""
    question: str = Field(description="Natural language question to convert to SQL")

class DatabaseSchemaInput(BaseModel):
    """Input schema for database schema inspection"""
    table_name: Optional[str] = Field(default=None, description="Specific table name to get schema for, or None for all tables")


class SQLAgentState(BaseAgentState):
    """State for SQL Agent extending base state"""
    sql_query: Optional[str]
    sql_data: Optional[List[Dict[str, Any]]]
    row_count: Optional[int]
    database_schema: Optional[str]

class SQLAgentResult(BaseAgentResult):
    """Result structure for SQL Agent"""
    def __init__(self, success: bool, sql_query: Optional[str] = None, 
                 data: Optional[List[Dict[str, Any]]] = None, 
                 row_count: Optional[int] = None,
                 explanation: Optional[str] = None,
                 error: Optional[str] = None):
        super().__init__(success, error)
        self.sql_query = sql_query
        self.data = data or []
        self.row_count = row_count or 0
        self.explanation = explanation
        self.agent_type = "sql"