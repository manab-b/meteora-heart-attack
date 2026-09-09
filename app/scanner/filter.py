from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PoolFilter:
    min_tvl_usd: float = 10_000
    min_volume_24h_usd: float = 50_000
    min_fee_24h_usd: float = 100
    max_age_seconds: float = 120

def eligible_pool(tvl_usd: float, volume_24h_usd: float,
                  fee_24h_usd: float, data_age_seconds: float,
                  cfg: PoolFilter = PoolFilter()) -> bool:
    return (
        tvl_usd >= cfg.min_tvl_usd
        and volume_24h_usd >= cfg.min_volume_24h_usd
        and fee_24h_usd >= cfg.min_fee_24h_usd
        and data_age_seconds <= cfg.max_age_seconds
    )
