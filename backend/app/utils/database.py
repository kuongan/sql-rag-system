"""
Utility functions moved from core
"""
import os
import json
import logging
from typing import Dict, Any, List, Optional
import sqlite3
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

def get_database_path() -> str:
    """Get the database file path"""
    return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "travel.sqlite")

def normalize_datetime(val: str) -> Optional[str]:
    """Normalize datetime to 'YYYY-MM-DD HH:MM:SS' format"""
    if not val or val == "\\N":
        return None
    try:
        clean_val = val.split("+")[0].strip()  # bỏ timezone
        # Trường hợp chỉ có ngày (book_date)
        if len(clean_val) == 10:  # YYYY-MM-DD
            dt = datetime.strptime(clean_val, "%Y-%m-%d")
        else:
            dt = datetime.fromisoformat(clean_val)
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return val


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
    """Execute SQL query safely with datetime normalization"""
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
        
        # xác định cột datetime theo table
        datetime_fields = {
            "flights": {"scheduled_departure", "scheduled_arrival", "actual_departure", "actual_arrival"},
            "bookings": {"book_date"}
        }
        
        # parse table name từ query (chỉ đơn giản lấy sau FROM)
        table_name = None
        tokens = query_upper.split()
        if "FROM" in tokens:
            table_name = tokens[tokens.index("FROM") + 1].lower()
        
        data = []
        for row in rows:
            row_dict = dict(row)
            if table_name in datetime_fields:
                for k in datetime_fields[table_name]:
                    if k in row_dict:
                        row_dict[k] = normalize_datetime(row_dict[k])
            data.append(row_dict)
        
        conn.close()
        
        return {
            "success": True,
            "query": query,
            "data": data,
            "row_count": len(data),
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

if __name__ == "__main__":
    db_path = get_database_path()

    # Test 1: Lấy vài dòng trong bookings để xem book_date có được normalize chưa
    result1 = execute_sql_query("SELECT book_ref, book_date, total_amount FROM bookings LIMIT 5;", db_path)
    print("Test 1 - Sample bookings:")
    print(result1)

    # Test 2: Thử group by month
    result2 = execute_sql_query("""
        SELECT strftime('%Y-%m', book_date) AS month, COUNT(*) AS num_bookings
        FROM bookings
        GROUP BY month
        ORDER BY month;
    """, db_path)
    print("Test 2 - Bookings per month:")
    print(result2)

    # Test 3: Kiểm tra NULL book_date
    result3 = execute_sql_query("SELECT COUNT(*) AS null_count FROM bookings WHERE book_date IS NULL;", db_path)
    print("Test 3 - NULL book_date count:")
    print(result3)