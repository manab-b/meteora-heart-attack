from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Any

from app.collector.meteora_api import MeteoraDataApiClient
from app.storage.raw import insert_raw_snapshot


def ingest_position_history_readonly(
    connection: sqlite3.Connection,
    client: MeteoraDataApiClient,
    position_address: str,
) -> dict[str, Any]:
    """Persist authoritative position events; never infer fees from pool volume."""
    observed_at = datetime.now(timezone.utc).isoformat()
    endpoint = f"/positions/{position_address}/historical"
    try:
        payload = client.get_position_history(position_address)
    except Exception as exc:
        insert_raw_snapshot(
            connection,
            source="meteora-data-api",
            endpoint=endpoint,
            pool_address=None,
            status="ERROR",
            error=f"{type(exc).__name__}: {exc}",
            observed_at=observed_at,
        )
        raise
    insert_raw_snapshot(
        connection,
        source="meteora-data-api",
        endpoint=endpoint,
        pool_address=None,
        payload=payload,
        observed_at=observed_at,
    )
    return payload
