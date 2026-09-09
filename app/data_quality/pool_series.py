from __future__ import annotations
import sqlite3

def latest_observations(conn: sqlite3.Connection, pool_address: str, limit: int=100):
    return conn.execute(
        "SELECT observed_at,payload_json FROM raw_pool_observations WHERE pool_address=? ORDER BY observed_at DESC LIMIT ?",
        (pool_address,limit)).fetchall()

def observation_count(conn: sqlite3.Connection, pool_address: str) -> int:
    return conn.execute("SELECT COUNT(*) FROM raw_pool_observations WHERE pool_address=?",
                        (pool_address,)).fetchone()[0]
