from __future__ import annotations

def pnl_sol(entry_price:float,exit_price:float,notional_sol:float)->float:
    if entry_price<=0 or exit_price<=0 or notional_sol<0: raise ValueError("invalid trade inputs")
    return notional_sol*(exit_price/entry_price-1)

def net_pnl(gross_pnl_sol:float,fees_sol:float)->float:
    if fees_sol<0: raise ValueError("fees must be non-negative")
    return gross_pnl_sol-fees_sol
