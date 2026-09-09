from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.collector.live_readonly import CollectionResult, collect_top_pools_readonly
from app.collector.meteora_api import MeteoraDataApiClient
from app.collector.pool_state import normalize_bin_liquidity
from app.storage.bin_snapshot import persist_bin_observations
from app.storage.raw import insert_raw_snapshot


@dataclass(frozen=True)
class ReadonlyPipelineResult:
    collection: CollectionResult
    bins_persisted: int


def collect_market_state_readonly(
    connection: sqlite3.Connection,
    client: MeteoraDataApiClient,
    *,
    limit: int = 20,
    page_size: int = 100,
    timeframe: str = "5m",
) -> ReadonlyPipelineResult:
    """Run discovery and normalize bin state when the API exposes it.

    No position fee is inferred from pool volume. Missing bin state is retained as
    a raw API observation and is intentionally not replaced with estimates.
    """
    collection = collect_top_pools_readonly(
        connection,
        client,
        limit=limit,
        page_size=page_size,
        timeframe=timeframe,
    )
    bins_persisted = 0
    for address in collection.pool_addresses:
        # Re-read the most recent pool payload already persisted by the collector.
        row = connection.execute(
            """
            SELECT payload_json, observed_at FROM raw_snapshots
            WHERE source = 'meteora-data-api'
              AND endpoint = ?
              AND status = 'OK'
              AND pool_address = ?
            ORDER BY id DESC LIMIT 1
            """,
            (f"/pools/{address}", address),
        ).fetchone()
        if row is None or row[0] is None:
            continue
        import json
        payload: dict[str, Any] = json.loads(row[0])
        try:
            observations = normalize_bin_liquidity(
                pool_address=address,
                payload=payload,
                observed_at=str(row[1]),
            )
        except (TypeError, ValueError):
            continue
        bins_persisted += persist_bin_observations(
            connection,
            observations,
            source="meteora-data-api",
        )
    return ReadonlyPipelineResult(collection=collection, bins_persisted=bins_persisted)
