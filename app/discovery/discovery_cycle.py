from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class DiscoveryConfig:
    min_tvl_usd: float=1_000
    min_volume_24h_usd: float=0
    max_pools: int=100

class DiscoveryCycle:
    def __init__(self, fetch_pools: Callable[[], object], config: DiscoveryConfig=DiscoveryConfig()):
        self.fetch_pools=fetch_pools
        self.config=config

    def run(self):
        from app.discovery.pool_discovery import discover
        from app.discovery.scoring import opportunity_score
        from app.discovery.watchlist import build_watchlist, WatchlistConfig
        candidates=discover(self.fetch_pools(),self.config.min_tvl_usd,self.config.min_volume_24h_usd)
        scores={p.address:opportunity_score(volume_24h_usd=p.volume_24h_usd,tvl_usd=p.tvl_usd,fee_24h_usd=p.fee_24h_usd) for p in candidates}
        selected=build_watchlist(candidates,WatchlistConfig(self.config.max_pools,self.config.min_tvl_usd,self.config.min_volume_24h_usd))
        return candidates,scores,selected
