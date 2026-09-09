from __future__ import annotations
from dataclasses import dataclass
from typing import Callable
from app.research.strategy_grid import StrategyConfig
from app.research.strategy_ranking import StrategyResult, rank

@dataclass(frozen=True)
class OptimizationResult:
    tested: int
    ranked: tuple[StrategyResult, ...]

def optimize(configs: list[StrategyConfig], evaluator: Callable[[StrategyConfig], StrategyResult]) -> OptimizationResult:
    results=[evaluator(c) for c in configs]
    return OptimizationResult(len(results), tuple(rank(results)))
