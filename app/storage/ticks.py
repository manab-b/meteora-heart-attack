from __future__ import annotations
import sqlite3
from app.collector.tick import Tick

SCHEMA = """
CREATE TABLE IF NOT EXISTS pool_ticks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_address TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    price REAL NOT NULL,
    active_bin INTEGER,
    tvl_usd REAL,
    dynamic_fee_pct REAL,
    source TEXT NOT NULL,
    data_age_seconds REAL
);
CREATE INDEX IF NOT EXISTS idx_pool_ticks_pool_time
ON pool_ticks(pool_address, observed_at);
"""

def init_tick_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()

def insert_tick(connection: sqlite3.Connection, tick: Tick) -> None:
    connection.execute(
        """INSERT INTO pool_ticks
        (pool_address, observed_at, price, active_bin, tvl_usd,
         dynamic_fee_pct, source, data_age_seconds)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
        (tick.pool_address, tick.observed_at, tick.price, tick.active_bin,
         tick.tvl_usd, tick.dynamic_fee_pct, tick.source, tick.data_age_seconds),
    )
    connection.commit()
