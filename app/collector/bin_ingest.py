from __future__ import annotations

import json
import sqlite3
from datetime import datetime
from typing import Any

from app.storage.bin_drain import record_bin_drain
from app.storage.bin_liquidity import insert_bin_liquidity
from app.storage.raw import insert_raw_snapshot


def _timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def ingest_bin_observation(connection: sqlite3.Connection, payload: dict[str, Any]) -> None:
    observed_at = str(payload["observed_at"])
    observed_ts = _timestamp(observed_at)
    pool_address = str(payload["pool_address"])
    bin_id = int(payload["bin_id"])
    active_bin_id = int(payload["active_bin_id"])
    x_amount_raw = str(payload["x_amount_raw"])
    y_amount_raw = str(payload["y_amount_raw"])
    insert_raw_snapshot(
        connection,
        source="meteora-sdk",
        endpoint="bin_collector",
        pool_address=pool_address,
        payload=payload,
        observed_at=observed_at,
    )
    insert_bin_liquidity(
        connection,
        pool_address=pool_address,
        bin_id=bin_id,
        active_bin_id=active_bin_id,
        price=str(payload["price"]),
        x_amount_raw=x_amount_raw,
        y_amount_raw=y_amount_raw,
        observed_at=observed_ts,
        source="meteora-sdk",
    )
    record_bin_drain(
        connection,
        pool_address=pool_address,
        bin_id=bin_id,
        active_bin_id=active_bin_id,
        x_amount_raw=x_amount_raw,
        y_amount_raw=y_amount_raw,
        observed_at=observed_ts,
        source="meteora-sdk",
    )


def ingest_jsonl(connection: sqlite3.Connection, lines) -> int:
    count = 0
    for line in lines:
        text = line.strip()
        if not text:
            continue
        payload = json.loads(text)
        if "error" in payload:
            continue
        ingest_bin_observation(connection, payload)
        count += 1
    connection.commit()
    return count
