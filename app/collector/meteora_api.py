from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any

import httpx


DEFAULT_BASE_URL = "https://dlmm.datapi.meteora.ag"


@dataclass(frozen=True)
class MeteoraApiConfig:
    base_url: str = DEFAULT_BASE_URL
    timeout_seconds: float = 15.0
    min_request_interval_seconds: float = 1.0 / 30.0


class MeteoraDataApiClient:
    """Read-only client for the official Meteora DLMM Data API.

    This client never signs, builds, or submits Solana transactions.
    """

    def __init__(self, config: MeteoraApiConfig = MeteoraApiConfig()) -> None:
        self.config = config
        self._client = httpx.Client(
            base_url=config.base_url.rstrip("/"),
            timeout=config.timeout_seconds,
            headers={"Accept": "application/json"},
        )
        self._last_request_at = 0.0

    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> "MeteoraDataApiClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def _get(self, path: str, **params: Any) -> dict[str, Any]:
        elapsed = time.monotonic() - self._last_request_at
        if elapsed < self.config.min_request_interval_seconds:
            time.sleep(self.config.min_request_interval_seconds - elapsed)
        response = self._client.get(path, params=params or None)
        self._last_request_at = time.monotonic()
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict):
            raise ValueError("Meteora API response must be a JSON object")
        return payload

    def get_pools(
        self,
        *,
        page: int = 1,
        page_size: int = 100,
        query: str | None = None,
        sort_by: str | None = None,
        filter_by: str | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "page_size": page_size}
        if query is not None:
            params["query"] = query
        if sort_by is not None:
            params["sort_by"] = sort_by
        if filter_by is not None:
            params["filter_by"] = filter_by
        return self._get("/pools", **params)

    def get_pool(self, address: str) -> dict[str, Any]:
        return self._get(f"/pools/{address}")

    def get_ohlcv(
        self,
        address: str,
        *,
        timeframe: str = "5m",
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {"timeframe": timeframe}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        return self._get(f"/pools/{address}/ohlcv", **params)

    def get_volume_history(
        self,
        address: str,
        *,
        start_time: int | None = None,
        end_time: int | None = None,
    ) -> dict[str, Any]:
        params: dict[str, Any] = {}
        if start_time is not None:
            params["start_time"] = start_time
        if end_time is not None:
            params["end_time"] = end_time
        return self._get(f"/pools/{address}/volume/history", **params)

    def get_position_history(self, position_address: str) -> dict[str, Any]:
        """Fetch authoritative add/remove/claim events for one DLMM position."""
        return self._get(f"/positions/{position_address}/historical")

    def get_position_pnl(self, pool_address: str) -> dict[str, Any]:
        """Fetch indexed PnL data for positions associated with a pool."""
        return self._get(f"/positions/{pool_address}/pnl")

    def get_wallet_pool_claims(self, wallet: str, pool_address: str) -> dict[str, Any]:
        """Fetch indexed accumulated fee/reward claims for a wallet and pool."""
        return self._get(f"/wallets/{wallet}/pools/{pool_address}/total_claims")


def json_dumps_stable(payload: dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
