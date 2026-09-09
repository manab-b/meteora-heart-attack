from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class RankedStrategy:
    strategy_key:str
    trades:int
    net_pnl:float
    profit_factor:float
    max_drawdown:float
    win_rate:float

def rank(rows:list[RankedStrategy])->list[RankedStrategy]:
    return sorted(rows,key=lambda x:(x.profit_factor,x.net_pnl,-x.max_drawdown,x.win_rate),reverse=True)
