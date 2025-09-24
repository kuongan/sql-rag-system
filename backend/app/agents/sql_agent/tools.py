"""
SQL Agent Tools - Using @tool decorator for proper function calling
"""
import logging
from typing import  Optional
from langchain_core.tools import tool
from pydantic import BaseModel, Field
from .prompts import SQL_GENERATION_PROMPT
from app.utils.database import get_database_path, get_database_schema, execute_sql_query
from app.utils.manager import get_llm
from app.models.agents.sql import SQLQueryInput, DatabaseSchemaInput

logger = logging.getLogger(__name__)

@tool("get_database_schema", args_schema=DatabaseSchemaInput, return_direct=True)
def get_database_schema_tool(table_name: Optional[str] = None) -> str:
    """
    Get database schema information. If table_name is provided, returns schema for that specific table.
    Otherwise returns schema for all tables.
    
    Args:
        table_name: Optional specific table name to inspect
        
    Returns:
        String containing database schema information
    """
    try:
        db_path = get_database_path()
        schema_info = get_database_schema(db_path)
        
        if table_name:
            if table_name in schema_info:
                table_info = schema_info[table_name]
                result = f"Schema for table '{table_name}':\n"
                result += "Columns:\n"
                for col in table_info['columns']:
                    result += f"  - {col['name']} ({col['type']})\n"
                result += f"\nSample data: {table_info['sample_data'][:3]}"
                return result
            else:
                return f"Table '{table_name}' not found in database. Available tables: {list(schema_info.keys())}"
        else:
            result = "Database Schema Overview:\n"
            for table, info in schema_info.items():
                result += f"\nTable: {table}\n"
                result += f"  Columns: {len(info['columns'])}\n"
                column_names = [col['name'] for col in info['columns']]
                result += f"  Column names: {', '.join(column_names)}\n"
                result += f"  Sample rows: {len(info['sample_data'])}\n"
            return result
            
    except Exception as e:
        logger.error(f"Error inspecting database schema: {e}")
        return f"Error getting database schema: {str(e)}"

@tool("execute_sql_query", args_schema=SQLQueryInput, return_direct=True)
def execute_sql_query_tool(question: str) -> str:
    """
    Convert natural language question to SQL query and execute it on the travel database.
    
    Args:
        question: Natural language question to convert to SQL
        
    Returns:
        String containing query results and execution details
    """
    try:
        db_path = get_database_path()
        schema_info = get_database_schema(db_path)
        
        # Create schema description for LLM
        schema_text = "Database Schema:\n"
        for table_name, table_info in schema_info.items():
            schema_text += f"\nTable: {table_name}\n"
            schema_text += "Columns:\n"
            for col in table_info['columns']:
                schema_text += f"  - {col['name']} ({col['type']})\n"
        
        # Generate SQL query using LLM
        llm = get_llm()
        
        sql_prompt = f"""
    {SQL_GENERATION_PROMPT}

    Database Schema:
    {schema_text}

    User Question: {question}

    Rules:
    - Only use columns that exist in the schema
    - For date-based queries, use actual date columns like `scheduled_departure` or `actual_departure`
    - Output only SELECT statements
    - Return results as JSON array suitable for visualization
    SQL Query:
    """
        
        response = llm.invoke(sql_prompt)
        sql_query = response.content.strip()
        
        # Clean the SQL query
        if sql_query.startswith('```sql'):
            sql_query = sql_query[6:]
        if sql_query.endswith('```'):
            sql_query = sql_query[:-3]
        
        sql_query = sql_query.strip()
        
        # Execute the query
        result = execute_sql_query(sql_query, db_path)
        
        if result['success']:
            response_text = f"Query executed successfully!\n\n"
            response_text += f"SQL Query: {sql_query}\n\n"
            response_text += f"Results ({result['row_count']} rows):\n"
            if result['data']:
                for i, row in enumerate(result['data'], 1):   # duyệt toàn bộ data
                    response_text += f"Row {i}: {row}\n"
            else:
                response_text += "No data returned\n"
            return response_text
        else:
            return f"Query failed: {result['error']}\nSQL Query attempted: {sql_query}"
            
    except Exception as e:
        logger.error(f"Error in SQL query execution: {e}")
        return f"Error executing SQL query: {str(e)}"

# Export tools list for easy access
SQL_TOOLS = [get_database_schema_tool, execute_sql_query_tool]


if __name__ == "__main__":
    print("=== TEST SQL TOOLS ===\n")

    schema = get_database_schema_tool.invoke({"table_name": None})
    print(schema)

    schema_table = get_database_schema_tool.invoke({"table_name": "flights"})
    print(schema_table)

    query_result = execute_sql_query_tool.invoke({"question": "List the first 5 flights with departure city and arrival city"})
    print(query_result)

    query_result = execute_sql_query_tool.invoke({"question": "How many bookings are there?"})
    print(query_result)
