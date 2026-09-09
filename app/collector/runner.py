from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any

from app.storage.raw import insert_raw_snapshot

from .endpoints import MeteoraDataApi


@dataclass(frozen=True)
class PoolPollResult:
    pool_address: str
    observed_at: str
    payload: dict[str, Any]


class PoolPoller:
    """One-shot read-only pool poller; scheduling stays outside the collector."""

    def __init__(self, api: MeteoraDataApi):
        self.api = api

    def poll(self, pool_address: str) -> PoolPollResult:
        observed_at = datetime.now(timezone.utc).isoformat()
        payload = self.api.pool(pool_address)
        if not isinstance(payload, dict):
            raise TypeError("pool endpoint must return an object")
        return PoolPollResult(pool_address, observed_at, payload)

    @staticmethod
    def persist_result(connection, result: PoolPollResult) -> None:
        insert_raw_snapshot(
            connection,
            source="meteora-data-api",
            endpoint=f"/pools/{result.pool_address}",
            pool_address=result.pool_address,
            observed_at=result.observed_at,
            payload=result.payload,
        )
