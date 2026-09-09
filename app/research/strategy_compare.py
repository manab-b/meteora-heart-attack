from __future__ import annotations
from dataclasses import dataclass
from app.research.strategy_grid import StrategyConfig
from app.research.strategy_ranking import StrategyResult, rank

@dataclass(frozen=True)
class Comparison:
    ranked: tuple[StrategyResult, ...]
    best: StrategyResult | None

def compare(results: list[StrategyResult]) -> Comparison:
    ranked=tuple(rank(results))
    return Comparison(ranked, ranked[0] if ranked else None)
