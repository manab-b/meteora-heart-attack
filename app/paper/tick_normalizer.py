from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class NormalizedTick:
    pool_address: str
    observed_at: float
    price: float
    volume_usd: float
    volume_usd_in_range: float
    seconds_out_of_range: int
    rug_flags: tuple[str,...]

def normalize_tick(pool_address: str, observed_at: float, raw: dict[str,Any],
                   previous_price: float|None=None, interval_seconds: int=30) -> NormalizedTick:
    price=float(raw.get("price") or raw.get("current_price") or 0)
    volume=float(raw.get("volume_usd") or raw.get("volume") or 0)
    if price <= 0: raise ValueError("invalid market price")
    return NormalizedTick(pool_address,observed_at,price,volume,volume,0,())
