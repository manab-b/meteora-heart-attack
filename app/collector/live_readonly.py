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


def _page_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    rows = payload.get("data", [])
    if not isinstance(rows, list):
        raise ValueError("unexpected /pools response: data must be a list")
    return [row for row in rows if isinstance(row, dict)]


def _has_next_page(payload: dict[str, Any], *, page: int, page_size: int) -> bool:
    pages = payload.get("pages")
    if isinstance(pages, int):
        return page < pages
    total = payload.get("total")
    if isinstance(total, int):
        return page * page_size < total
    return len(_page_rows(payload)) >= page_size


def collect_top_pools_readonly(
    connection: sqlite3.Connection,
    client: MeteoraDataApiClient,
    *,
    limit: int = 20,
    page_size: int = 100,
    sort_by: str = "volume_24h:desc",
    timeframe: str = "5m",
) -> CollectionResult:
    """Discover and persist real Meteora API payloads; never derives fake fees."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    if page_size <= 0:
        raise ValueError("page_size must be positive")

    addresses: list[str] = []
    seen: set[str] = set()
    discovered = 0
    page = 1

    while len(addresses) < limit:
        payload = client.get_pools(page=page, page_size=page_size, sort_by=sort_by)
        observed_at = datetime.now(timezone.utc).isoformat()
        insert_raw_snapshot(
            connection,
            source="meteora-data-api",
            endpoint="/pools",
            pool_address=None,
            payload=payload,
            observed_at=observed_at,
        )
        rows = _page_rows(payload)
        discovered += len(rows)

        for row in rows:
            address = row.get("address") or row.get("publicKey")
            if not address:
                continue
            address = str(address)
            if address in seen:
                continue
            seen.add(address)
            addresses.append(address)
            if len(addresses) >= limit:
                break

        if len(addresses) >= limit or not rows or not _has_next_page(payload, page=page, page_size=page_size):
            break
        page += 1

    succeeded = 0
    failed = 0
    for address in addresses:
        try:
            ingest_pool_readonly(connection, client, address, timeframe=timeframe)
            succeeded += 1
        except Exception:
            # ingest_pool_readonly already stores the authoritative API error snapshot.
            # Keep discovery resilient so one bad pool cannot stop the research batch.
            failed += 1

    return CollectionResult(
        discovered=discovered,
        attempted=len(addresses),
        succeeded=succeeded,
        failed=failed,
        pool_addresses=tuple(addresses),
    )
