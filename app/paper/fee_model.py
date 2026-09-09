from __future__ import annotations

def fee_usd_from_volume(volume_usd: float, fee_rate: float) -> float:
    if volume_usd < 0 or fee_rate < 0: raise ValueError("volume and fee_rate must be non-negative")
    return volume_usd*fee_rate

def fee_sol_from_usd(fee_usd: float, sol_price_usd: float) -> float:
    if fee_usd < 0 or sol_price_usd <= 0: raise ValueError("invalid fee or SOL price")
    return fee_usd/sol_price_usd
