from __future__ import annotations
from dataclasses import dataclass
from typing import Callable, Any
from app.research.strategy_grid import StrategyConfig, StrategyResult

@dataclass(frozen=True)
class EvaluationContext:
    initial_sol: float = 5.0

def evaluate(config: StrategyConfig, ticks: list[Any], simulator: Callable[[StrategyConfig,list[Any],EvaluationContext], StrategyResult],
             context: EvaluationContext=EvaluationContext()) -> StrategyResult:
    return simulator(config,ticks,context)
