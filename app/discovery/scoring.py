from __future__ import annotations
def opportunity_score(*, volume_24h_usd: float, tvl_usd: float, fee_24h_usd: float) -> float:
    if tvl_usd <= 0: return 0.0
    turnover=volume_24h_usd/tvl_usd
    fee_yield=fee_24h_usd/tvl_usd
    return turnover*0.7 + fee_yield*0.3
