from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from app.positions.analytics import consecutive_range_survival, position_fee_delta
from app.positions.adapter import normalize_position
from app.storage.position_analytics import insert_position_analytics
from app.storage.raw import insert_raw_snapshot


def _timestamp(value: str) -> float:
    text = value.replace("Z", "+00:00")
    return datetime.fromisoformat(text).timestamp()


def _latest_analytics(connection: sqlite3.Connection, position_address: str):
    return connection.execute(
        """SELECT observed_at, range_survival_seconds, fee_x_delta_raw, fee_y_delta_raw
        FROM position_analytics
        WHERE position_address = ?
        ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (position_address,),
    ).fetchone()


def ingest_position_observation(
    connection: sqlite3.Connection,
    payload: dict[str, Any],
) -> dict[str, Any]:
    """Persist one JSONL SDK observation and derive only observable metrics.

    Fee SOL is intentionally left NULL here: a real token/SOL quote must be
    supplied by the valuation layer before converting raw fee deltas to SOL.
    """
    observed_at = str(payload["observed_at"])
    observed_ts = _timestamp(observed_at)
    snapshot = normalize_position(payload, observed_at, source="meteora-sdk")
    insert_raw_snapshot(
        connection,
        source="meteora-sdk",
        endpoint="position_collector",
        pool_address=snapshot.pool_address,
        payload=payload,
        observed_at=observed_at,
    )

    previous = connection.execute(
        """SELECT unclaimed_fee_x, unclaimed_fee_y, observed_at
        FROM position_snapshots
        WHERE position_address = ?
        ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (snapshot.position_address,),
    ).fetchone()
    insert_position = connection.execute
    insert_position(
        """INSERT INTO position_snapshots
        (position_address,owner,pool_address,lower_bin_id,upper_bin_id,
         deposited_x,deposited_y,unclaimed_fee_x,unclaimed_fee_y,observed_at,source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?)""",
        (
            snapshot.position_address,
            snapshot.owner,
            snapshot.pool_address,
            snapshot.lower_bin_id,
            snapshot.upper_bin_id,
            snapshot.deposited_x,
            snapshot.deposited_y,
            snapshot.unclaimed_fee_x,
            snapshot.unclaimed_fee_y,
            snapshot.observed_at,
            snapshot.source,
        ),
    )

    previous_analytics = _latest_analytics(connection, snapshot.position_address)
    if previous:
        fee_x_delta, fee_y_delta, reset_or_claim = position_fee_delta(
            previous[0], previous[1], snapshot.unclaimed_fee_x, snapshot.unclaimed_fee_y
        )
        elapsed = max(0.0, observed_ts - _timestamp(previous[2]))
    else:
        fee_x_delta, fee_y_delta, reset_or_claim = 0, 0, False
        elapsed = 0.0

    previous_survival = float(previous_analytics[1]) if previous_analytics else 0.0
    active_bin = payload.get("active_bin_id")
    if active_bin is not None and snapshot.lower_bin_id is not None and snapshot.upper_bin_id is not None:
        survival = consecutive_range_survival(
            previous_survival,
            elapsed,
            int(active_bin),
            snapshot.lower_bin_id,
            snapshot.upper_bin_id,
        )
        in_range = snapshot.lower_bin_id <= int(active_bin) <= snapshot.upper_bin_id
    else:
        survival = 0.0
        in_range = None

    insert_position_analytics(
        connection,
        position_address=snapshot.position_address,
        pool_address=snapshot.pool_address,
        observed_at=observed_ts,
        active_bin_id=int(active_bin) if active_bin is not None else None,
        lower_bin_id=snapshot.lower_bin_id,
        upper_bin_id=snapshot.upper_bin_id,
        in_range=in_range,
        range_survival_seconds=survival,
        fee_x_delta_raw=fee_x_delta,
        fee_y_delta_raw=fee_y_delta,
        reset_or_claim=reset_or_claim,
        fee_sol=None,
        source="meteora-sdk",
    )
    connection.commit()
    return {
        "position_address": snapshot.position_address,
        "pool_address": snapshot.pool_address,
        "fee_x_delta_raw": fee_x_delta,
        "fee_y_delta_raw": fee_y_delta,
        "reset_or_claim": reset_or_claim,
        "range_survival_seconds": survival,
        "in_range": in_range,
    }


def ingest_jsonl(connection: sqlite3.Connection, lines) -> list[dict[str, Any]]:
    results = []
    for line in lines:
        text = line.strip()
        if not text:
            continue
        payload = json.loads(text)
        if "error" in payload:
            continue
        results.append(ingest_position_observation(connection, payload))
    return results
