from __future__ import annotations
from statistics import median
from app.strategy.backtest import Trade

def summarize(trades: list[Trade]) -> dict:
    if not trades:
        return {"trades": 0, "median_fee_sol": 0.0, "median_hold_seconds": 0.0}
    holds = [max(0.0, t.exit_timestamp - t.entry_timestamp) for t in trades]
    fees = [t.fee_sol for t in trades]
    return {
        "trades": len(trades),
        "median_fee_sol": median(fees),
        "median_hold_seconds": median(holds),
        "exit_reasons": {
            reason: sum(1 for t in trades if t.exit_reason == reason)
            for reason in sorted({t.exit_reason for t in trades})
        },
    }
