from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Candidate:
    pool_address:str
    strategy_key:str
    median_pnl:float
    p05_pnl:float
    max_drawdown_sol:float
    consistency:float
    accepted:bool

def rank(candidates:list[Candidate])->list[Candidate]:
    return sorted(candidates,key=lambda x:(x.accepted,x.p05_pnl,x.median_pnl,x.consistency,-x.max_drawdown_sol),reverse=True)
