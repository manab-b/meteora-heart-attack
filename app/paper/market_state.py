from __future__ import annotations
from dataclasses import dataclass

@dataclass
class MarketState:
    price: float
    previous_price: float|None = None
    out_of_range_seconds: int = 0
    in_range_volume_usd: float = 0.0
    total_volume_usd: float = 0.0
    fee_usd: float = 0.0
    liquidity_usd: float = 0.0
    liquidity_change_pct: float = 0.0
    rug_flags: tuple[str,...] = ()

def update_state(state: MarketState, *, price: float, min_price: float, max_price: float,
                 volume_usd: float, fee_usd: float=0.0, liquidity_usd: float=0.0,
                 interval_seconds: int=30, drain_threshold_pct: float=-40.0) -> MarketState:
    if price <= 0 or volume_usd < 0: raise ValueError("invalid market tick")
    in_range=min_price <= price <= max_price
    out_seconds=0 if in_range else state.out_of_range_seconds+interval_seconds
    in_vol=state.in_range_volume_usd+(volume_usd if in_range else 0.0)
    change=0.0
    if state.liquidity_usd>0 and liquidity_usd>0: change=(liquidity_usd/state.liquidity_usd-1)*100
    flags=list(state.rug_flags)
    if change <= drain_threshold_pct and "LIQUIDITY_DRAIN" not in flags: flags.append("LIQUIDITY_DRAIN")
    return MarketState(price,state.price,out_seconds,in_vol,state.total_volume_usd+volume_usd,
                       state.fee_usd+fee_usd,liquidity_usd,change,tuple(flags))
