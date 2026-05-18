'''
SQLite garden DB util functions
Independent from streamlit dependencies for offline module use.
'''


import sqlite3
from pathlib import Path


DB_PATH = Path(__file__).parent.parent / "data" / "garden.db"

def get_connection() -> sqlite3.Connection:
    '''
    Create a single SQLite connection.
 
    Returns:
    sqlite3.Connection- A shared connection with foreign key enforcement enabled and
    row_factory set to sqlite3.Row for column-name access.
    '''
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")
    conn.row_factory = sqlite3.Row
    return conn
 
