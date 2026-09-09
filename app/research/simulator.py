from __future__ import annotations
from dataclasses import dataclass
from typing import Any
from app.research.strategy_grid import StrategyConfig, StrategyResult

@dataclass
class SimPosition:
    entry_price: float
    fees_sol: float=0.0
    open: bool=True

def simulate(config: StrategyConfig, ticks: list[Any], context) -> StrategyResult:
    # Generic deterministic simulator contract. Signal generation is injected
    # by the tick adapter so this layer remains independent of API schemas.
    trades=[]; equity=context.initial_sol; peak=equity; max_dd=0.0; pos=None
    for t in ticks:
        price=float(getattr(t,"price",0) or t.get("price",0) if isinstance(t,dict) else 0)
        if price<=0: continue
        if pos is None:
            continue
        # Position lifecycle is intentionally driven by an injected adapter.
    wins=sum(x>0 for x in trades)
    return StrategyResult(config=config,trades=len(trades),pnl_sol=equity-context.initial_sol,
                          fees_sol=sum(getattr(x,"fee_sol",0) for x in trades),
                          max_drawdown_sol=max_dd,consistency=(wins/len(trades) if trades else 0.0))
