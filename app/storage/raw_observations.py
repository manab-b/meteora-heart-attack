from __future__ import annotations
import json, sqlite3, time

def ensure_raw_observations(conn:sqlite3.Connection)->None:
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS raw_pool_observations(
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      pool_address TEXT NOT NULL,
      observed_at REAL NOT NULL,
      payload_json TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_raw_pool_time
      ON raw_pool_observations(pool_address,observed_at);
    """)

def insert_observation(conn, pool_address:str, payload:dict, observed_at:float|None=None)->None:
    ensure_raw_observations(conn)
    with conn:
        conn.execute("INSERT INTO raw_pool_observations(pool_address,observed_at,payload_json) VALUES(?,?,?)",
                     (pool_address,observed_at or time.time(),json.dumps(payload,separators=(",",":"))))
