from __future__ import annotations
import sqlite3
from .model import PositionSnapshot

SCHEMA = """
CREATE TABLE IF NOT EXISTS position_snapshots (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_address TEXT NOT NULL,
    owner TEXT NOT NULL,
    pool_address TEXT NOT NULL,
    lower_bin_id INTEGER,
    upper_bin_id INTEGER,
    deposited_x TEXT NOT NULL,
    deposited_y TEXT NOT NULL,
    unclaimed_fee_x TEXT NOT NULL,
    unclaimed_fee_y TEXT NOT NULL,
    observed_at TEXT NOT NULL,
    source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_position_snapshots
ON position_snapshots(position_address, observed_at);
"""

def init_position_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()

def insert_position(connection: sqlite3.Connection, snapshot: PositionSnapshot) -> None:
    connection.execute(
        """INSERT INTO position_snapshots
        (position_address, owner, pool_address, lower_bin_id, upper_bin_id,
         deposited_x, deposited_y, unclaimed_fee_x, unclaimed_fee_y, observed_at, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (snapshot.position_address, snapshot.owner, snapshot.pool_address,
         snapshot.lower_bin_id, snapshot.upper_bin_id, snapshot.deposited_x,
         snapshot.deposited_y, snapshot.unclaimed_fee_x, snapshot.unclaimed_fee_y,
         snapshot.observed_at, snapshot.source),
    )
    connection.commit()
