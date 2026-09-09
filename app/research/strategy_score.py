from __future__ import annotations

def score_strategy(median_pnl: float, p05_pnl: float, max_drawdown: float,
                   loss_probability: float, median_fee_sol: float) -> float:
    # Conservative research score: reward repeatable fees and downside,
    # penalize drawdown and probability of losing money.
    raw = (
        0.30 * median_pnl +
        0.30 * p05_pnl +
        0.15 * median_fee_sol -
        0.15 * max_drawdown -
        0.10 * loss_probability
    )
    return raw
