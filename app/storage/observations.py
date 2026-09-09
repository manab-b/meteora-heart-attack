from __future__ import annotations
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS observations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pool_address TEXT NOT NULL,
    bins INTEGER NOT NULL,
    timestamp REAL NOT NULL,
    price REAL NOT NULL,
    volume_usd REAL NOT NULL,
    fee_velocity_sol_min REAL NOT NULL,
    drain_score REAL NOT NULL,
    range_survival_seconds REAL NOT NULL,
    in_range INTEGER NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_obs_pool_time
ON observations(pool_address, bins, timestamp);
"""

def init_observation_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()

def insert_observation(connection: sqlite3.Connection, pool_address: str, bins: int,
                       timestamp: float, price: float, volume_usd: float,
                       fee_velocity_sol_min: float, drain_score: float,
                       range_survival_seconds: float, in_range: bool) -> None:
    connection.execute(
        """INSERT INTO observations
        (pool_address,bins,timestamp,price,volume_usd,fee_velocity_sol_min,
         drain_score,range_survival_seconds,in_range)
        VALUES (?,?,?,?,?,?,?,?,?)""",
        (pool_address,bins,timestamp,price,volume_usd,fee_velocity_sol_min,
         drain_score,range_survival_seconds,int(in_range))
    )
    connection.commit()
