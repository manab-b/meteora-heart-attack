from __future__ import annotations

import sqlite3

from app.metrics.pool_drain import PoolDrainSummary, aggregate_pool_drain


def latest_pool_drain(
    connection: sqlite3.Connection,
    pool_address: str,
    *,
    lookback_seconds: float = 300.0,
    top_n: int = 5,
) -> PoolDrainSummary:
    if lookback_seconds <= 0:
        raise ValueError("lookback_seconds must be positive")
    row = connection.execute(
        "SELECT MAX(observed_at) FROM bin_drain_events WHERE pool_address = ?",
        (pool_address,),
    ).fetchone()
    latest = row[0] if row else None
    if latest is None:
        return PoolDrainSummary(pool_address, 0.0, 0.0, 0.0, 0, 0)

    rows = connection.execute(
        """
        SELECT pool_address, score, active_bin_moved
        FROM bin_drain_events
        WHERE pool_address = ? AND observed_at >= ?
        ORDER BY observed_at DESC
        """,
        (pool_address, float(latest) - lookback_seconds),
    ).fetchall()

    events = [
        type("StoredDrainEvent", (), {
            "pool_address": row[0],
            "score": row[1],
            "active_bin_moved": bool(row[2]),
        })()
        for row in rows
    ]
    return aggregate_pool_drain(pool_address, events, top_n=top_n)
