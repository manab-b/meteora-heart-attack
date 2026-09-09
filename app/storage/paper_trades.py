from __future__ import annotations
import sqlite3

def ensure_paper_trades(conn):
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS paper_trades(
      id INTEGER PRIMARY KEY AUTOINCREMENT,pool_address TEXT NOT NULL,strategy_key TEXT NOT NULL,
      entry_at REAL NOT NULL,exit_at REAL,entry_price REAL NOT NULL,exit_price REAL,
      gross_pnl_sol REAL DEFAULT 0,fees_sol REAL DEFAULT 0,net_pnl_sol REAL DEFAULT 0,
      exit_reason TEXT,metadata_json TEXT
    );
    CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy ON paper_trades(strategy_key);
    """)

def record_trade(conn,**t):
    ensure_paper_trades(conn)
    keys=("pool_address","strategy_key","entry_at","exit_at","entry_price","exit_price","gross_pnl_sol","fees_sol","net_pnl_sol","exit_reason","metadata_json")
    with conn:
        conn.execute("INSERT INTO paper_trades("+",".join(keys)+") VALUES("+",".join("?" for _ in keys)+")",[t.get(k) for k in keys])
