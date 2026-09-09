from __future__ import annotations


def research_score(row: dict) -> float:
    """Rank paper-trading candidates using fees, net PnL and downside risk."""
    trades = int(row.get("trades", 0))
    if trades < 5:
        return float("-inf")
    median_fee = max(0.0, float(row.get("median_fee_sol", 0.0)))
    total_fee = max(0.0, float(row.get("total_fee_sol", 0.0)))
    hold = max(1.0, float(row.get("median_hold_seconds", 0.0)))
    fee_rate = (median_fee * 0.7 + total_fee * 0.3) / hold * 60.0
    median_net_pnl = float(row.get("median_net_pnl_sol", 0.0))
    p05_net_pnl = float(row.get("p05_net_pnl_sol", 0.0))
    median_drawdown = max(0.0, float(row.get("median_max_drawdown_sol", 0.0)))
    p95_drawdown = max(0.0, float(row.get("p95_max_drawdown_sol", 0.0)))
    negative_prob = min(1.0, max(0.0, float(row.get("probability_negative_pnl", 0.0))))
    pnl_component = max(-1.0, median_net_pnl) + 0.5 * max(-1.0, p05_net_pnl)
    drawdown_penalty = 0.35 * median_drawdown + 0.65 * p95_drawdown
    return (fee_rate + pnl_component - drawdown_penalty) / (1.0 + negative_prob)


def rank_results(rows: list[dict], limit: int = 20) -> list[dict]:
    if limit <= 0:
        return []
    return sorted(rows, key=research_score, reverse=True)[:limit]
