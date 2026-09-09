from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class StrategyObservation:
    strategy_key:str; pool_address:str; timestamp:float; score:float; entry:bool; exit:bool
def group_by_strategy(rows):
    out={}
    for r in rows: out.setdefault(r.strategy_key,[]).append(r)
    return out
