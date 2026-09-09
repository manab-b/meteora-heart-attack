from __future__ import annotations
from dataclasses import dataclass
from .http import MeteoraHttpClient
from .rate_limit import RateLimiter

@dataclass(frozen=True)
class PoolCandidate:
    address: str
    raw: dict

class PoolDiscovery:
    def __init__(self, client: MeteoraHttpClient, requests_per_second: float = 20.0):
        self.client = client
        self.limiter = RateLimiter(requests_per_second)

    def list_pools(self, page_size: int = 1000) -> list[PoolCandidate]:
        self.limiter.wait()
        payload = self.client.get_json("/pools", {"page": "1", "page_size": str(page_size)})
        items = payload.get("data", payload if isinstance(payload, list) else [])
        return [PoolCandidate(str(item.get("address", item.get("publicKey", ""))), item) for item in items]
