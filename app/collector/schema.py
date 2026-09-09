from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PoolSnapshot:
    pool_address: str
    price: float
    tvl_usd: float
    volume_24h_usd: float
    fee_24h_usd: float
    active_bin_id: int | None
    observed_at: str
    source: str = "meteora"

@dataclass(frozen=True)
class BinSnapshot:
    pool_address: str
    bin_id: int
    price: float
    liquidity_x: str
    liquidity_y: str
    fee_x: str
    fee_y: str
    observed_at: str
    source: str = "meteora"

@dataclass(frozen=True)
class CollectorBatch:
    pool: PoolSnapshot
    bins: tuple[BinSnapshot, ...]
