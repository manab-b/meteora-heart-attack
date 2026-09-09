from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PositionHealth:
    fee_sol_per_minute: float
    estimated_fee_sol: float
    estimated_il_pct: float
    range_seconds: float
    drain_score: float
    net_score: float

def health_score(fee_sol_per_minute: float, estimated_il_pct: float,
                 range_seconds: float, drain_score: float) -> float:
    fee = max(fee_sol_per_minute, 0.0)
    survival = min(max(range_seconds, 0.0) / 300.0, 1.0)
    il_penalty = min(abs(min(estimated_il_pct, 0.0)) / 10.0, 1.0)
    safety = 1.0 - min(max(drain_score, 0.0), 1.0)
    return fee * (0.5 + 0.5 * survival) * safety * (1.0 - 0.5 * il_penalty)
