from __future__ import annotations
from dataclasses import dataclass
from app.metrics.score import opportunity_score

@dataclass(frozen=True)
class OpportunityRow:
    pool_address: str
    bins: int
    fee_sol_min: float
    range_survival_seconds: float
    drain_score: float
    score: float

def build_rows(pool_address: str, fee_by_bins: dict[int, float],
               survival_by_bins: dict[int, float], drain_score: float) -> list[OpportunityRow]:
    rows = []
    for bins, fee in fee_by_bins.items():
        survival = survival_by_bins.get(bins, 0.0)
        rows.append(OpportunityRow(
            pool_address, bins, fee, survival, drain_score,
            opportunity_score(fee, survival, drain_score)
        ))
    return sorted(rows, key=lambda x: x.score, reverse=True)
