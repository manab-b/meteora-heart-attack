from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable
from app.research.strategy_grid import StrategyConfig

@dataclass(frozen=True)
class StrategyResult:
    config: StrategyConfig
    trades: int
    total_pnl: float
    median_pnl: float
    max_drawdown: float
    loss_probability: float
    score: float

def rank(results: Iterable[StrategyResult]) -> list[StrategyResult]:
    return sorted(results, key=lambda r:(r.score,r.median_pnl,r.total_pnl), reverse=True)
