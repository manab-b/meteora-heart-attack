from __future__ import annotations
import sqlite3

def ensure_strategy_tables(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS strategy_runs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      strategy_key TEXT NOT NULL,
      bin_step_bps INTEGER NOT NULL,
      num_bins INTEGER NOT NULL,
      min_score REAL NOT NULL,
      max_drain REAL NOT NULL,
      trades INTEGER NOT NULL DEFAULT 0,
      total_pnl REAL NOT NULL DEFAULT 0,
      median_pnl REAL NOT NULL DEFAULT 0,
      max_drawdown REAL NOT NULL DEFAULT 0,
      loss_probability REAL NOT NULL DEFAULT 0,
      score REAL NOT NULL DEFAULT 0,
      created_at TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_strategy_runs_score ON strategy_runs(score DESC);
    """)
