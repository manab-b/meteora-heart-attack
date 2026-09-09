from __future__ import annotations

import sqlite3

from app.metrics.bin_drain_history import BinLiquidityPoint, compare_bin_snapshots


def init_bin_drain_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS bin_drain_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool_address TEXT NOT NULL,
            bin_id INTEGER NOT NULL,
            previous_observed_at REAL NOT NULL,
            observed_at REAL NOT NULL,
            elapsed_seconds REAL NOT NULL,
            active_bin_moved INTEGER NOT NULL,
            depletion_ratio REAL NOT NULL,
            score REAL NOT NULL,
            source TEXT NOT NULL,
            UNIQUE(pool_address, bin_id, observed_at)
        );
        CREATE INDEX IF NOT EXISTS idx_bin_drain_events_time
        ON bin_drain_events(pool_address, bin_id, observed_at);
        """
    )


def record_bin_drain(
    connection: sqlite3.Connection,
    *,
    pool_address: str,
    bin_id: int,
    active_bin_id: int,
    x_amount_raw: str,
    y_amount_raw: str,
    observed_at: float,
    source: str,
) -> bool:
    existing = connection.execute(
        """
        SELECT 1 FROM bin_drain_events
        WHERE pool_address = ? AND bin_id = ? AND observed_at = ?
        LIMIT 1
        """,
        (pool_address, bin_id, observed_at),
    ).fetchone()
    if existing is not None:
        return False

    row = connection.execute(
        """
        SELECT active_bin_id, x_amount_raw, y_amount_raw, observed_at
        FROM bin_liquidity_snapshots
        WHERE pool_address = ? AND bin_id = ? AND observed_at < ?
        ORDER BY observed_at DESC
        LIMIT 1
        """,
        (pool_address, bin_id, observed_at),
    ).fetchone()
    if row is None:
        return False

    previous = BinLiquidityPoint(
        pool_address=pool_address,
        bin_id=bin_id,
        active_bin_id=int(row[0]),
        x_amount_raw=int(row[1]),
        y_amount_raw=int(row[2]),
        observed_at=float(row[3]),
    )
    current = BinLiquidityPoint(
        pool_address=pool_address,
        bin_id=bin_id,
        active_bin_id=active_bin_id,
        x_amount_raw=int(x_amount_raw),
        y_amount_raw=int(y_amount_raw),
        observed_at=observed_at,
    )
    event = compare_bin_snapshots(previous, current)
    connection.execute(
        """
        INSERT OR IGNORE INTO bin_drain_events
        (pool_address, bin_id, previous_observed_at, observed_at, elapsed_seconds,
         active_bin_moved, depletion_ratio, score, source)
        VALUES (?,?,?,?,?,?,?,?,?)
        """,
        (
            event.pool_address,
            event.bin_id,
            event.previous_observed_at,
            event.observed_at,
            event.elapsed_seconds,
            int(event.active_bin_moved),
            event.depletion_ratio,
            event.score,
            source,
        ),
    )
    return connection.execute("SELECT changes()").fetchone()[0] == 1
