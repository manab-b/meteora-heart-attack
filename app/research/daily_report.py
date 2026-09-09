from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DailyReport:
    trades: int
    closed: int
    total_pnl: float
    median_pnl: float
    max_drawdown: float
    loss_probability: float
    score: float

def build_report(trades:int, closed:int, total_pnl:float, median_pnl:float,
                 max_drawdown:float, loss_probability:float, score:float)->DailyReport:
    return DailyReport(trades,closed,total_pnl,median_pnl,max_drawdown,loss_probability,score)
