from __future__ import annotations
import time
from dataclasses import dataclass
from app.adapters.meteora_dlmm import MeteoraDLMMClient
from app.adapters.meteora_normalize import PoolObservation, normalize_pool

@dataclass(frozen=True)
class CollectorConfig:
    interval_seconds: int = 30
    limit: int = 100

class MeteoraCollector:
    def __init__(self, client: MeteoraDLMMClient, config: CollectorConfig=CollectorConfig()):
        self.client=client
        self.config=config

    def collect_pools(self) -> list[PoolObservation]:
        response=self.client.pools(limit=self.config.limit)
        data=response.data
        items=data.get("data",data) if isinstance(data,dict) else data
        if not isinstance(items,list):
            raise ValueError("unexpected /pools response shape")
        return [normalize_pool(x,response.fetched_at) for x in items if isinstance(x,dict)]

    def collect_pool(self,address:str) -> PoolObservation:
        response=self.client.pool(address)
        return normalize_pool(response.data,response.fetched_at)
