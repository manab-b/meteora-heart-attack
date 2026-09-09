from __future__ import annotations

import sqlite3

from app.collector.pool_state import BinLiquidityObservation
from app.storage.bin_drain import record_bin_drain
from app.storage.bin_liquidity import insert_bin_liquidity
from app.storage.raw import insert_raw_snapshot


def persist_bin_observations(
    connection: sqlite3.Connection,
    observations: list[BinLiquidityObservation],
    *,
    source: str = "meteora-readonly",
    raw_payload: dict | None = None,
) -> int:
    """Persist normalized bins and derive drain events only from consecutive snapshots."""
    if not observations:
        return 0
    pool_address = observations[0].pool_address
    observed_at = observations[0].observed_at
    if any(row.pool_address != pool_address or row.observed_at != observed_at for row in observations):
        raise ValueError("all bin observations must belong to one pool and timestamp")

    if raw_payload is not None:
        insert_raw_snapshot(
            connection,
            source=source,
            endpoint="bin_state",
            pool_address=pool_address,
            payload=raw_payload,
            observed_at=observed_at,
        )

    from datetime import datetime
    observed_ts = datetime.fromisoformat(observed_at.replace("Z", "+00:00")).timestamp()
    for row in observations:
        insert_bin_liquidity(
            connection,
            pool_address=row.pool_address,
            bin_id=row.bin_id,
            active_bin_id=row.active_bin_id,
            price=row.price,
            x_amount_raw=row.x_amount_raw,
            y_amount_raw=row.y_amount_raw,
            observed_at=observed_ts,
            source=source,
        )
        record_bin_drain(
            connection,
            pool_address=row.pool_address,
            bin_id=row.bin_id,
            active_bin_id=row.active_bin_id,
            x_amount_raw=row.x_amount_raw,
            y_amount_raw=row.y_amount_raw,
            observed_at=observed_ts,
            source=source,
        )
    connection.commit()
    return len(observations)
