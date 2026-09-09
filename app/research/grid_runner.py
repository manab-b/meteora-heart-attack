from __future__ import annotations
from dataclasses import dataclass
from app.research.metrics import summarize
from app.research.strategy_grid import StrategyConfig
@dataclass(frozen=True)
class StrategyResult:
    config:StrategyConfig; metrics:dict[str,float]
def evaluate(config:StrategyConfig,pnls:list[float])->StrategyResult:
    return StrategyResult(config,summarize(pnls))
def rank_results(results:list[StrategyResult]):
    return sorted(results,key=lambda r:(r.metrics["profit_factor"],r.metrics["net_pnl"],-r.metrics["max_drawdown"]),reverse=True)
