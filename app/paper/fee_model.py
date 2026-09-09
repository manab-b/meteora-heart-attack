from __future__ import annotations
def fee_sol_from_usd(fee_usd: float, sol_price_usd: float) -> float:
    if sol_price_usd <= 0: raise ValueError("sol_price_usd must be positive")
    return max(0.0, fee_usd) / sol_price_usd

def lp_fee_usd(volume_usd: float, fee_rate: float, lp_share: float) -> float:
    if volume_usd < 0: raise ValueError("volume_usd must be non-negative")
    if not 0 <= fee_rate: raise ValueError("fee_rate must be non-negative")
    if not 0 <= lp_share <= 1: raise ValueError("lp_share must be within [0,1]")
    return volume_usd * fee_rate * lp_share
