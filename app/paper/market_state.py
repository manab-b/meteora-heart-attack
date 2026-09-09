from __future__ import annotations
from dataclasses import dataclass

@dataclass
class MarketState:
    last_price: float | None = None
    out_of_range_seconds: int = 0
    cumulative_volume_usd: float = 0.0
    cumulative_fee_usd: float = 0.0
    liquidity_usd: float = 0.0
    rug_flags: tuple[str,...] = ()

    def update(self, *, price: float, in_range: bool, volume_usd: float,
               fee_usd: float=0.0, liquidity_usd: float=0.0,
               interval_seconds: int=30, rug_flags: tuple[str,...]=()) -> None:
        self.last_price=price
        self.out_of_range_seconds = 0 if in_range else self.out_of_range_seconds + interval_seconds
        self.cumulative_volume_usd += max(0.0, volume_usd)
        self.cumulative_fee_usd += max(0.0, fee_usd)
        self.liquidity_usd=liquidity_usd
        self.rug_flags=rug_flags
