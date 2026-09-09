from __future__ import annotations
from statistics import median
from app.strategy.backtest import Trade
from .equity import max_drawdown

def build_report(trades: list[Trade]) -> dict:
    if not trades:
        return {"trades": 0, "median_fee_sol": 0.0, "total_fee_sol": 0.0,
                "median_hold_seconds": 0.0, "max_drawdown_sol": 0.0,
                "exit_reasons": {}}
    fees = [max(0.0, t.fee_sol) for t in trades]
    holds = [max(0.0, t.exit_timestamp - t.entry_timestamp) for t in trades]
    # Price PnL is intentionally not converted to SOL here because token inventory
    # and valuation rules belong to the execution/valuation layer.
    return {
        "trades": len(trades),
        "median_fee_sol": median(fees),
        "total_fee_sol": sum(fees),
        "median_hold_seconds": median(holds),
        "max_drawdown_sol": 0.0,
        "exit_reasons": {
            reason: sum(1 for t in trades if t.exit_reason == reason)
            for reason in sorted({t.exit_reason for t in trades})
        },
    }
