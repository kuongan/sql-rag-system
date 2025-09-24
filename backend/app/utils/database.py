"""
Utility functions moved from core
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import sqlite3
from pathlib import Path

logger = logging.getLogger(__name__)

def get_database_path() -> str:
    """Get the database file path"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "travel.sqlite")

def get_database_schema(db_path: str) -> Dict[str, Any]:
    """Get database schema information"""
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
        tables = cursor.fetchall()
        
        schema_info = {}
        for table in tables:
            table_name = table[0]
            
            # Get table info
            cursor.execute(f"PRAGMA table_info({table_name});")
            columns = cursor.fetchall()
            
            # Get sample data
            cursor.execute(f"SELECT * FROM {table_name} LIMIT 3;")
            sample_data = cursor.fetchall()
            
            schema_info[table_name] = {
                "columns": [{"name": col[1], "type": col[2], "nullable": not col[3]} for col in columns],
                "sample_data": sample_data
            }
        
        conn.close()
        return schema_info
        
    except Exception as e:
        logger.error(f"Error getting database schema: {e}")
        return {}

def execute_sql_query(query: str, db_path: str) -> Dict[str, Any]:
    """Execute SQL query safely"""
    try:
        dangerous_keywords = ['DROP', 'DELETE', 'INSERT', 'UPDATE', 'ALTER', 'CREATE']
        query_upper = query.upper()
        
        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return {
                    "success": False,
                    "error": f"Query contains potentially dangerous keyword: {keyword}",
                    "data": [],
                    "row_count": 0
                }
        
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute(query)
        rows = cursor.fetchall()
        
        # Convert to list of dictionaries
        data = [dict(row) for row in rows]
        row_count = len(data)
        
        conn.close()
        
        return {
            "success": True,
            "query": query,
            "data": data,
            "row_count": row_count,
            "error": None
        }
        
    except Exception as e:
        logger.error(f"Error executing SQL query: {e}")
        return {
            "success": False,
            "error": str(e),
            "data": [],
            "row_count": 0
        }
