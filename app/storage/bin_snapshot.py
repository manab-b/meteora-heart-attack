from __future__ import annotations

import sqlite3
from typing import Any, Iterable

from app.collector.pool_state import BinLiquidityObservation
from app.storage.bin_drain import record_bin_drain
from app.storage.bin_liquidity import insert_bin_liquidity
from app.storage.raw import insert_raw_snapshot


def persist_bin_observations(
    connection: sqlite3.Connection,
    observations: Iterable[BinLiquidityObservation],
    *,
    source: str,
    raw_payload: dict[str, Any] | None = None,
) -> int:
    rows = list(observations)
    if not rows:
        return 0
    for row in rows:
        from datetime import datetime
        observed_ts = datetime.fromisoformat(row.observed_at.replace("Z", "+00:00")).timestamp()
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
    if raw_payload is not None:
        insert_raw_snapshot(
            connection,
            source=source,
            endpoint="bin_snapshot",
            pool_address=rows[0].pool_address,
            payload=raw_payload,
            observed_at=rows[0].observed_at,
        )
    connection.commit()
    return len(rows)
