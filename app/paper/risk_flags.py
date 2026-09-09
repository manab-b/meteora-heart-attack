from __future__ import annotations
def detect(*, liquidity_now: float, liquidity_prev: float|None,
           price_change_pct: float, volume_usd: float,
           min_liquidity_ratio: float=0.35,
           max_price_change_pct: float=35.0) -> tuple[str,...]:
    flags=[]
    if liquidity_prev and liquidity_now/liquidity_prev < min_liquidity_ratio:
        flags.append("LIQUIDITY_SHOCK")
    if abs(price_change_pct) >= max_price_change_pct:
        flags.append("PRICE_SHOCK")
    if liquidity_now <= 0:
        flags.append("LIQUIDITY_ZERO")
    if volume_usd <= 0 and liquidity_prev and liquidity_now < liquidity_prev:
        flags.append("LIQUIDITY_DRAIN_NO_VOLUME")
    return tuple(flags)
