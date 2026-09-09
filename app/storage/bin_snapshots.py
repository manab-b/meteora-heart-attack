from __future__ import annotations
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS bin_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_address TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    active_bin_id INTEGER NOT NULL,
    active_bin_price REAL NOT NULL,
    bin_id INTEGER NOT NULL,
    bin_price REAL NOT NULL,
    x_amount TEXT NOT NULL,
    y_amount TEXT NOT NULL,
    source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_bin_snapshots_pool_time
ON bin_snapshots(pool_address, observed_at);
"""

def init_bin_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()

def insert_bin_snapshot(
    connection: sqlite3.Connection,
    *,
    pool_address: str,
    observed_at: str,
    active_bin_id: int,
    active_bin_price: float,
    bin_id: int,
    bin_price: float,
    x_amount: str,
    y_amount: str,
    source: str = "meteora-sdk",
) -> None:
    connection.execute(
        """INSERT INTO bin_snapshots
        (pool_address, observed_at, active_bin_id, active_bin_price,
         bin_id, bin_price, x_amount, y_amount, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (pool_address, observed_at, active_bin_id, active_bin_price,
         bin_id, bin_price, x_amount, y_amount, source),
    )
    connection.commit()
