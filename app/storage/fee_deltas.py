from __future__ import annotations

import sqlite3


def init_fee_delta_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS position_fee_observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_address TEXT NOT NULL,
            pool_address TEXT NOT NULL,
            observed_at REAL NOT NULL,
            fee_x REAL NOT NULL,
            fee_y REAL NOT NULL,
            fee_sol REAL,
            source TEXT NOT NULL
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_position_fee_obs ON position_fee_observations(position_address, observed_at)"
    )
    connection.commit()


def insert_fee_observation(
    connection: sqlite3.Connection,
    *,
    position_address: str,
    pool_address: str,
    observed_at: float,
    fee_x: float,
    fee_y: float,
    fee_sol: float | None,
    source: str,
) -> None:
    if fee_x < 0 or fee_y < 0:
        raise ValueError("fee values must be non-negative")
    connection.execute(
        """
        INSERT INTO position_fee_observations
        (position_address,pool_address,observed_at,fee_x,fee_y,fee_sol,source)
        VALUES (?,?,?,?,?,?,?)
        """,
        (position_address, pool_address, observed_at, fee_x, fee_y, fee_sol, source),
    )
    connection.commit()


def latest_fee_observation(connection: sqlite3.Connection, position_address: str):
    return connection.execute(
        """
        SELECT position_address,pool_address,observed_at,fee_x,fee_y,fee_sol,source
        FROM position_fee_observations
        WHERE position_address = ?
        ORDER BY observed_at DESC, id DESC
        LIMIT 1
        """,
        (position_address,),
    ).fetchone()
