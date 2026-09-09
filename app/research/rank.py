from __future__ import annotations

def research_score(row: dict) -> float:
    trades = row.get("trades", 0)
    if trades < 5:
        return float("-inf")
    median_fee = max(0.0, row.get("median_fee_sol", 0.0))
    total_fee = max(0.0, row.get("total_fee_sol", 0.0))
    hold = max(1.0, row.get("median_hold_seconds", 0.0))
    return (median_fee * 0.7 + total_fee * 0.3) / hold * 60.0

def rank_results(rows: list[dict], limit: int = 20) -> list[dict]:
    return sorted(rows, key=research_score, reverse=True)[:limit]
