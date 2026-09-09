from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class TradeOutcome:
    position_id: str
    entry_value_usd: float
    exit_value_usd: float
    fees_sol: float
    sol_price_usd: float
    pnl_usd: float
    return_pct: float
    hodl_value_usd: float
    vs_hodl_usd: float

def evaluate_trade(position_id: str, entry_x: float, entry_y: float,
                   exit_x: float, exit_y: float, entry_x_price: float,
                   entry_y_price: float, exit_x_price: float, exit_y_price: float,
                   fees_sol: float, sol_price_usd: float) -> TradeOutcome:
    entry_value = entry_x*entry_x_price + entry_y*entry_y_price
    exit_value = exit_x*exit_x_price + exit_y*exit_y_price
    if entry_value <= 0: raise ValueError("entry value must be positive")
    if min(exit_x, exit_y, entry_x, entry_y, fees_sol) < 0 or sol_price_usd <= 0:
        raise ValueError("invalid trade inputs")
    fee_value = fees_sol * sol_price_usd
    pnl = exit_value - entry_value + fee_value
    hodl = entry_x*exit_x_price + entry_y*exit_y_price
    return TradeOutcome(position_id, entry_value, exit_value, fees_sol, sol_price_usd,
                        pnl, pnl/entry_value*100, hodl, exit_value+fee_value-hodl)
