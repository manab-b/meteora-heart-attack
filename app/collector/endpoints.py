from __future__ import annotations

from typing import Any

from .http import MeteoraHttpClient
from .rate_limit import RateLimiter


class MeteoraDataApi:
    """Read-only wrapper around Meteora's indexed DLMM Data API."""

    def __init__(self, client: MeteoraHttpClient, requests_per_second: float = 20.0):
        self.client = client
        self.limiter = RateLimiter(requests_per_second)

    def pool(self, address: str) -> dict[str, Any]:
        return self._get(f"/pools/{address}")

    def ohlcv(self, address: str, *, timeframe: str = "5m", start: int | None = None, end: int | None = None) -> Any:
        params = {"timeframe": timeframe}
        if start is not None:
            params["start"] = str(start)
        if end is not None:
            params["end"] = str(end)
        return self._get(f"/pools/{address}/ohlcv", params)

    def volume_history(self, address: str, *, timeframe: str = "5m", start: int | None = None, end: int | None = None) -> Any:
        params = {"timeframe": timeframe}
        if start is not None:
            params["start"] = str(start)
        if end is not None:
            params["end"] = str(end)
        return self._get(f"/pools/{address}/volume/history", params)

    def _get(self, path: str, params: dict[str, str] | None = None) -> Any:
        self.limiter.wait()
        return self.client.get_json(path, params)
