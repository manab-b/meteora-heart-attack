from __future__ import annotations

def score_pool(fee_velocity_sol_min: float, range_survival_seconds: float,
               drain_score: float) -> float:
    survival = min(max(range_survival_seconds, 0.0) / 300.0, 1.0)
    safety = max(0.0, 1.0 - min(max(drain_score, 0.0), 1.0))
    return fee_velocity_sol_min * (0.5 + 0.5 * survival) * safety
