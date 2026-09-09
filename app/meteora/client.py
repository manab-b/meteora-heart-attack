from __future__ import annotations
from typing import Any
import httpx

class MeteoraAPIError(RuntimeError):
    pass

class MeteoraClient:
    def __init__(self, base_url: str = "https://dlmm.datapi.meteora.ag", timeout: float = 15.0):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout

    def list_pools(self, *, page: int = 1, page_size: int = 1000,
                   sort_by: str = "volume_24h:desc",
                   filter_by: str | None = None,
                   query: str | None = None) -> dict[str, Any]:
        params: dict[str, Any] = {"page": page, "page_size": page_size, "sort_by": sort_by}
        if filter_by:
            params["filter_by"] = filter_by
        if query:
            params["query"] = query
        try:
            response = httpx.get(f"{self.base_url}/pools", params=params, timeout=self.timeout)
            response.raise_for_status()
            payload = response.json()
        except (httpx.HTTPError, ValueError) as exc:
            raise MeteoraAPIError(f"Failed to fetch pools: {exc}") from exc
        if not isinstance(payload, dict) or not isinstance(payload.get("data"), list):
            raise MeteoraAPIError("Unexpected /pools response shape")
        return payload

    def iter_pools(self, **kwargs):
        page = 1
        while True:
            payload = self.list_pools(page=page, **kwargs)
            yield from payload["data"]
            pages = int(payload.get("pages", page))
            if page >= pages:
                break
            page += 1
