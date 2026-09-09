from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.collector.meteora_api import MeteoraDataApiClient
from app.collector.meteora_ingest import ingest_pool_readonly
from app.storage.raw import insert_raw_snapshot


@dataclass(frozen=True)
class CollectionResult:
    discovered: int
    attempted: int
    succeeded: int
    failed: int
    pool_addresses: tuple[str, ...]


def collect_top_pools_readonly(
    connection: sqlite3.Connection,
    client: MeteoraDataApiClient,
    *,
    limit: int = 20,
    page_size: int = 100,
    sort_by: str = "volume_24h:desc",
    timeframe: str = "5m",
) -> CollectionResult:
    """Discover and persist real Meteora API payloads; never derives tradeable state."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    payload = client.get_pools(page=1, page_size=page_size, sort_by=sort_by)
    observed_at = datetime.now(timezone.utc).isoformat()
    insert_raw_snapshot(
        connection,
        source="meteora-data-api",
        endpoint="/pools",
        pool_address=None,
        payload=payload,
        observed_at=observed_at,
    )

    rows = payload.get("data", []) if isinstance(payload, dict) else []
    if not isinstance(rows, list):
        raise ValueError("unexpected /pools response: data must be a list")

    addresses: list[str] = []
    for row in rows:
        if not isinstance(row, dict):
            continue
        address = row.get("address") or row.get("publicKey")
        if address:
            addresses.append(str(address))
        if len(addresses) >= limit:
            break

    succeeded = 0
    failed = 0
    for address in addresses:
        try:
            ingest_pool_readonly(connection, client, address, timeframe=timeframe)
            succeeded += 1
        except Exception:
            failed += 1

    return CollectionResult(
        discovered=len(rows),
        attempted=len(addresses),
        succeeded=succeeded,
        failed=failed,
        pool_addresses=tuple(addresses),
    )
