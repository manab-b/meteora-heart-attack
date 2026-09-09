from __future__ import annotations
import sqlite3, json, time
from app.discovery.pool_discovery import PoolCandidate

def ensure_watchlist(conn: sqlite3.Connection) -> None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS pool_watchlist (
      pool_address TEXT PRIMARY KEY,
      tvl_usd REAL NOT NULL,
      volume_24h_usd REAL NOT NULL,
      fee_24h_usd REAL NOT NULL,
      score REAL NOT NULL,
      updated_at REAL NOT NULL,
      payload_json TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_watchlist_score ON pool_watchlist(score DESC);
    """)

def replace_watchlist(conn: sqlite3.Connection, candidates: list[PoolCandidate], scores: dict[str,float]) -> None:
    ensure_watchlist(conn)
    now=time.time()
    with conn:
        conn.execute("DELETE FROM pool_watchlist")
        conn.executemany(
            "INSERT INTO pool_watchlist VALUES(?,?,?,?,?,?,?)",
            [(p.address,p.tvl_usd,p.volume_24h_usd,p.fee_24h_usd,scores.get(p.address,0),now,json.dumps(p.raw,separators=(",",":"))) for p in candidates])
