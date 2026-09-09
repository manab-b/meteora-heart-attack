from __future__ import annotations

import sqlite3


def init_bin_liquidity_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS bin_liquidity_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool_address TEXT NOT NULL,
            bin_id INTEGER NOT NULL,
            active_bin_id INTEGER NOT NULL,
            price TEXT NOT NULL,
            x_amount_raw TEXT NOT NULL,
            y_amount_raw TEXT NOT NULL,
            observed_at REAL NOT NULL,
            source TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_bin_liquidity_time
        ON bin_liquidity_snapshots(pool_address, bin_id, observed_at);
        """
    )


def insert_bin_liquidity(
    connection: sqlite3.Connection,
    *,
    pool_address: str,
    bin_id: int,
    active_bin_id: int,
    price: str,
    x_amount_raw: str,
    y_amount_raw: str,
    observed_at: float,
    source: str,
) -> None:
    if int(bin_id) < 0 and int(active_bin_id) < 0:
        # Negative bin IDs are valid on DLMM; this branch intentionally does nothing.
        pass
    connection.execute(
        """INSERT INTO bin_liquidity_snapshots
        (pool_address,bin_id,active_bin_id,price,x_amount_raw,y_amount_raw,observed_at,source)
        VALUES (?,?,?,?,?,?,?,?)""",
        (pool_address, bin_id, active_bin_id, price, x_amount_raw, y_amount_raw, observed_at, source),
    )
