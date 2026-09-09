from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.collector.meteora_api import MeteoraDataApiClient
from app.storage.raw import insert_raw_snapshot


def ingest_pool_readonly(
    connection: sqlite3.Connection,
    client: MeteoraDataApiClient,
    pool_address: str,
    *,
    timeframe: str = "5m",
    start_time: int | None = None,
    end_time: int | None = None,
) -> dict[str, Any]:
    """Fetch and persist authoritative Meteora API payloads without deriving fake fees."""
    observed_at = datetime.now(timezone.utc).isoformat()
    result: dict[str, Any] = {}

    for endpoint_name, fetch in (
        ("pool", lambda: client.get_pool(pool_address)),
        (
            "ohlcv",
            lambda: client.get_ohlcv(
                pool_address,
                timeframe=timeframe,
                start_time=start_time,
                end_time=end_time,
            ),
        ),
        ("volume_history", lambda: client.get_volume_history(pool_address)),
    ):
        endpoint = f"/pools/{pool_address}" if endpoint_name == "pool" else f"/pools/{pool_address}/{endpoint_name.replace('_', '/')}"
        try:
            payload = fetch()
        except Exception as exc:
            insert_raw_snapshot(
                connection,
                source="meteora-data-api",
                endpoint=endpoint,
                pool_address=pool_address,
                status="ERROR",
                error=f"{type(exc).__name__}: {exc}",
                observed_at=observed_at,
            )
            raise
        insert_raw_snapshot(
            connection,
            source="meteora-data-api",
            endpoint=endpoint,
            pool_address=pool_address,
            payload=payload,
            observed_at=observed_at,
        )
        result[endpoint_name] = payload

    return result
