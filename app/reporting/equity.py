from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EquityPoint:
    timestamp: float
    cumulative_fee_sol: float
    cumulative_price_pnl_sol: float
    cumulative_net_pnl_sol: float

def max_drawdown(points: list[EquityPoint]) -> float:
    peak = 0.0
    max_dd = 0.0
    for p in points:
        peak = max(peak, p.cumulative_net_pnl_sol)
        max_dd = max(max_dd, peak - p.cumulative_net_pnl_sol)
    return max_dd
