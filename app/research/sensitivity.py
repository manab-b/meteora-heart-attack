from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class SensitivityCell:
    parameter:str; value:float; trades:int; profit_factor:float; net_pnl:float; max_drawdown:float
def rank(cells:list[SensitivityCell]):
    return sorted(cells,key=lambda x:(x.profit_factor,x.net_pnl,-x.max_drawdown),reverse=True)
def stable_values(cells:list[SensitivityCell],min_pf:float=1.1):
    return [c for c in cells if c.profit_factor>=min_pf]
