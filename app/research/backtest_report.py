from __future__ import annotations
from dataclasses import dataclass
from app.research.strategy_ranking import rank, StrategyResult

@dataclass(frozen=True)
class BacktestReport:
    tested: int
    ranked: list[StrategyResult]

def build_report(results: list[StrategyResult]) -> BacktestReport:
    return BacktestReport(len(results),rank(results))
