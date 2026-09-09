from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EquityPoint:
    observed_at: float
    equity_sol: float

@dataclass(frozen=True)
class RiskStats:
    total_return_sol: float
    max_drawdown_sol: float
    max_drawdown_pct: float
    win_rate: float
    trades: int

def calculate(points: list[EquityPoint], trade_pnls: list[float]) -> RiskStats:
    if not points: return RiskStats(0,0,0,0,len(trade_pnls))
    peak=points[0].equity_sol; max_dd=0.0
    for p in points:
        peak=max(peak,p.equity_sol); max_dd=max(max_dd,peak-p.equity_sol)
    start=points[0].equity_sol
    dd_pct=(max_dd/start*100) if start>0 else 0.0
    wins=sum(x>0 for x in trade_pnls)
    return RiskStats(points[-1].equity_sol-start,max_dd,dd_pct,wins/len(trade_pnls) if trade_pnls else 0,len(trade_pnls))
