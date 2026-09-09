from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class NetPnl:
    entry_value_usd: float
    exit_value_usd: float
    fees_sol: float
    sol_price_usd: float
    fee_value_usd: float
    pnl_usd: float
    return_pct: float

def calculate_net_pnl(entry_value_usd: float, exit_value_usd: float, fees_sol: float, sol_price_usd: float) -> NetPnl:
    if entry_value_usd <= 0: raise ValueError('entry_value_usd must be positive')
    if exit_value_usd < 0 or fees_sol < 0 or sol_price_usd <= 0: raise ValueError('invalid valuation')
    fee_value_usd = fees_sol * sol_price_usd
    pnl_usd = exit_value_usd - entry_value_usd + fee_value_usd
    return NetPnl(entry_value_usd, exit_value_usd, fees_sol, sol_price_usd, fee_value_usd, pnl_usd, pnl_usd / entry_value_usd * 100)

def impermanent_loss_pct(entry_x: float, entry_y: float, exit_x: float, exit_y: float, entry_x_price: float, entry_y_price: float, exit_x_price: float, exit_y_price: float) -> float:
    entry = entry_x * entry_x_price + entry_y * entry_y_price
    exit_value = exit_x * exit_x_price + exit_y * exit_y_price
    if entry <= 0: raise ValueError('entry value must be positive')
    hodl = entry_x * exit_x_price + entry_y * exit_y_price
    return (exit_value / hodl - 1) * 100 if hodl > 0 else 0.0