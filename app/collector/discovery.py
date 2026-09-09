from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .http import MeteoraHttpClient
from .rate_limit import RateLimiter


@dataclass(frozen=True)
class PoolCandidate:
    address: str
    raw: dict[str, Any]


class PoolDiscovery:
    def __init__(self, client: MeteoraHttpClient, requests_per_second: float = 20.0):
        self.client = client
        self.limiter = RateLimiter(requests_per_second)

    def list_pools(self, page_size: int = 1000, max_pages: int | None = None) -> list[PoolCandidate]:
        if page_size <= 0:
            raise ValueError("page_size must be positive")
        results: list[PoolCandidate] = []
        page = 1
        while max_pages is None or page <= max_pages:
            self.limiter.wait()
            payload = self.client.get_json(
                "/pools", {"page": str(page), "page_size": str(page_size)}
            )
            items, pages = self._page_items(payload)
            for item in items:
                address = str(item.get("address") or item.get("publicKey") or "")
                if address:
                    results.append(PoolCandidate(address, item))
            if not items or (pages is not None and page >= pages) or len(items) < page_size:
                break
            page += 1
        return results

    @staticmethod
    def _page_items(payload: Any) -> tuple[list[dict[str, Any]], int | None]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)], None
        if not isinstance(payload, dict):
            return [], None
        items = payload.get("data") or payload.get("items") or payload.get("pools") or []
        if not isinstance(items, list):
            items = []
        pages = payload.get("pages") or payload.get("total_pages") or payload.get("totalPages")
        try:
            pages = int(pages) if pages is not None else None
        except (TypeError, ValueError):
            pages = None
        return [item for item in items if isinstance(item, dict)], pages
