from __future__ import annotations
import sqlite3
from app.storage.migrations import migrate

def open_database(path:str)->sqlite3.Connection:
    conn=sqlite3.connect(path,check_same_thread=False)
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA busy_timeout=5000")
    migrate(conn)
    return conn
