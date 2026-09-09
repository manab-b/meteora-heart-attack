from __future__ import annotations
import sqlite3

def ensure_results(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS strategy_results (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pool_address TEXT NOT NULL,
      strategy_key TEXT NOT NULL,
      trades INTEGER NOT NULL,
      pnl_sol REAL NOT NULL,
      fees_sol REAL NOT NULL,
      max_drawdown_sol REAL NOT NULL,
      consistency REAL NOT NULL,
      created_at REAL NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_strategy_results_rank
      ON strategy_results(pool_address, pnl_sol DESC);
    """)
