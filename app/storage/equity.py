from __future__ import annotations
import sqlite3,time

def ensure_equity(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS equity_snapshots(
      id INTEGER PRIMARY KEY AUTOINCREMENT,observed_at REAL NOT NULL,pool_address TEXT,
      strategy_key TEXT,equity_sol REAL NOT NULL,fees_sol REAL NOT NULL)""")

def record_equity(conn,equity_sol,fees_sol,pool_address=None,strategy_key=None):
    ensure_equity(conn)
    with conn:
        conn.execute("INSERT INTO equity_snapshots(observed_at,pool_address,strategy_key,equity_sol,fees_sol) VALUES(?,?,?,?,?)",(time.time(),pool_address,strategy_key,equity_sol,fees_sol))
