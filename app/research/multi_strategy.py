from __future__ import annotations
from dataclasses import dataclass
from app.research.strategy_grid import StrategyConfig

@dataclass
class StrategyState:
    key: str
    config: StrategyConfig
    pnl: float = 0.0
    fees_sol: float = 0.0
    trades: int = 0
    open_positions: int = 0

class MultiStrategyBook:
    def __init__(self, configs: list[StrategyConfig]):
        self.states={f"s{i+1}": StrategyState(f"s{i+1}",c) for i,c in enumerate(configs)}

    def record(self, key: str, pnl: float, fees_sol: float, opened: bool=False, closed: bool=False):
        s=self.states[key]
        s.pnl += pnl; s.fees_sol += fees_sol
        if opened: s.open_positions += 1
        if closed: s.open_positions=max(0,s.open_positions-1); s.trades += 1

    def snapshot(self): return list(self.states.values())
