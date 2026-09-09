from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class MarketTick:
    pool_address: str
    observed_at: float
    price: float
    volume_usd: float
    volume_usd_in_range: float = 0.0
    seconds_out_of_range: int = 0
    rug_flags: tuple[str,...] = ()
