from __future__ import annotations
from dataclasses import dataclass
from app.discovery.pool_discovery import PoolCandidate

@dataclass(frozen=True)
class WatchlistConfig:
    max_pools: int = 100
    min_tvl_usd: float = 1_000
    min_volume_24h_usd: float = 0

def build_watchlist(candidates: list[PoolCandidate], config: WatchlistConfig=WatchlistConfig()) -> list[str]:
    ranked=sorted(candidates,key=lambda p:(p.volume_24h_usd,p.fee_24h_usd,p.tvl_usd),reverse=True)
    return [p.address for p in ranked[:config.max_pools]]
