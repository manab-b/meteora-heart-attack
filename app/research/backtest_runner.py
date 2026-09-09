from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
from app.research.parameter_search import configs
from app.research.evaluator import EvaluationContext, evaluate
from app.research.strategy_grid import StrategyResult

@dataclass(frozen=True)
class BacktestSummary:
    tested: int
    results: list[StrategyResult]

class BacktestRunner:
    def __init__(self, simulator: Callable):
        self.simulator=simulator

    def run(self, ticks: list[Any], strategy_configs=None, context=EvaluationContext()) -> BacktestSummary:
        cfgs=strategy_configs if strategy_configs is not None else configs()
        results=[evaluate(c,ticks,self.simulator,context) for c in cfgs]
        return BacktestSummary(len(results),results)
