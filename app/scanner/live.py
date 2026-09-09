from __future__ import annotations

import sqlite3

from app.scanner.rank import Candidate, rank
from app.storage.pool_drain import latest_pool_drain


def _latest_observation(connection: sqlite3.Connection, pool_address: str):
    return connection.execute(
        """
        SELECT volume_usd, fee_velocity_sol_min, range_survival_seconds, in_range
        FROM observations
        WHERE pool_address = ?
        ORDER BY timestamp DESC
        LIMIT 1
        """,
        (pool_address,),
    ).fetchone()


def scan_paper_opportunities(
    connection: sqlite3.Connection,
    pool_addresses: list[str],
    *,
    limit: int = 20,
    drain_lookback_seconds: float = 300.0,
) -> list[Candidate]:
    """Build ranked paper-only candidates from persisted observations.

    The scanner never creates transactions or accesses private keys. A pool is
    omitted when no authoritative observation exists or when its latest state
    is out of range. Drain is read from the recent bin-level event history.
    """
    if limit <= 0:
        raise ValueError("limit must be positive")

    candidates: list[Candidate] = []
    for pool_address in dict.fromkeys(pool_addresses):
        row = _latest_observation(connection, pool_address)
        if row is None or not bool(row[3]):
            continue
        drain = latest_pool_drain(
            connection,
            pool_address,
            lookback_seconds=drain_lookback_seconds,
        )
        candidates.append(
            Candidate(
                pool_address=pool_address,
                volume_usd=float(row[0]),
                fee_sol_per_minute=float(row[1]),
                range_survival_seconds=float(row[2]),
                drain_score=drain.score,
            )
        )
    return rank(candidates, limit=limit)
