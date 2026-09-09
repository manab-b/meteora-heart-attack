from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class EquityPoint:
    timestamp:float; equity_sol:float; drawdown_sol:float; peak_sol:float
def build_equity(closed_trades,initial_sol=0.0):
    equity=peak=initial_sol; out=[]
    for t in sorted(closed_trades,key=lambda x:x.exit_at):
        equity+=t.net_pnl_sol; peak=max(peak,equity)
        out.append(EquityPoint(t.exit_at,equity,peak-equity,peak))
    return out
