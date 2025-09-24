#!/usr/bin/env python3
"""
Ingest SQLite to SQL Database (simplified)
Migrate data from SQLite to target SQL database
"""

import os
import sqlite3
import time
from sqlalchemy import create_engine, text

# ---------------------------
# Database utilities
# ---------------------------

def get_database_url():
    """Get target database URL from env or fallback to SQLite"""
    return os.getenv("DATABASE_URL", "sqlite:///data/main_database.db")

def connect_sqlite(sqlite_path: str):
    """Connect to source SQLite database"""
    if not os.path.exists(sqlite_path):
        raise FileNotFoundError(f"SQLite file not found: {sqlite_path}")
    conn = sqlite3.connect(sqlite_path)
    conn.row_factory = sqlite3.Row
    return conn

def get_sqlite_tables(conn):
    """Get list of tables in SQLite"""
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    return [row[0] for row in cursor.fetchall()]

def get_table_data(conn, table_name: str):
    """Read all rows from a table"""
    cursor = conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    columns = [desc[0] for desc in cursor.description]
    rows = [dict(zip(columns, row)) for row in cursor.fetchall()]
    return rows, columns

def create_target_table(engine, table_name: str, sample_row: dict):
    """Create table in target DB based on a sample row"""
    def get_sql_type(value):
        if isinstance(value, int):
            return "INTEGER"
        if isinstance(value, float):
            return "REAL"
        return "TEXT"

    columns = [f"{col} {get_sql_type(val)}" for col, val in sample_row.items()]
    create_sql = f"CREATE TABLE IF NOT EXISTS {table_name} ({', '.join(columns)})"
    with engine.begin() as conn:
        conn.execute(text(create_sql))

def insert_data(engine, table_name: str, data: list, columns: list):
    """Insert data into target DB in batches"""
    if not data:
        return
    placeholders = ", ".join([f":{c}" for c in columns])
    sql = f"INSERT OR REPLACE INTO {table_name} ({', '.join(columns)}) VALUES ({placeholders})"
    batch_size = 1000
    with engine.begin() as conn:
        for i in range(0, len(data), batch_size):
            conn.execute(text(sql), data[i:i+batch_size])

# ---------------------------
# Migration workflow
# ---------------------------

def migrate_database(sqlite_path: str, target_db_url: str):
    """Migrate entire SQLite DB to target DB"""
    sqlite_conn = connect_sqlite(sqlite_path)
    engine = create_engine(target_db_url)

    tables = get_sqlite_tables(sqlite_conn)
    for table in tables:
        data, columns = get_table_data(sqlite_conn, table)
        if not data:
            continue
        create_target_table(engine, table, data[0])
        insert_data(engine, table, data, columns)
        print(f"✅ Migrated {table} ({len(data)} rows)")

    sqlite_conn.close()
    engine.dispose()

# ---------------------------
# Entry point
# ---------------------------

def main():
    sqlite_path = "data/travel.sqlite"
    target_db_url = get_database_url()
    migrate_database(sqlite_path, target_db_url)
    print("🎉 Migration complete!")

if __name__ == "__main__":
    main()
