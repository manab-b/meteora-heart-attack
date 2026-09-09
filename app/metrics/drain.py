from __future__ import annotations

def liquidity_drain_score(previous_total: float, current_total: float) -> float:
    if previous_total <= 0:
        return 0.0
    drop = (previous_total - current_total) / previous_total
    return max(0.0, min(1.0, drop))
