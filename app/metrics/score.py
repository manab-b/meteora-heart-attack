from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Opportunity:
    pool_address: str
    fee_sol_per_minute: float
    range_survival_seconds: float
    drain_score: float
    score: float

def opportunity_score(fee_sol_per_minute: float,
                       range_survival_seconds: float,
                       drain_score: float,
                       execution_cost_sol: float = 0.0) -> float:
    survival = min(max(range_survival_seconds, 0.0) / 300.0, 1.0)
    safety = 1.0 - min(max(drain_score, 0.0), 1.0)
    net_fee = max(0.0, fee_sol_per_minute - execution_cost_sol)
    return net_fee * (0.5 + 0.5 * survival) * safety
