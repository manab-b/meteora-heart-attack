from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class RobustGate:
    min_test_trades:int=20
    min_test_pf:float=1.1
    max_test_dd:float=0.30
    min_train_test_ratio:float=0.50
def passes(train:dict,test:dict,g:RobustGate=RobustGate()):
    trades=int(test.get("trades",0)); pf=float(test.get("profit_factor",0)); dd=float(test.get("max_drawdown",0)); train_pf=float(train.get("profit_factor",0))
    ratio=0 if train_pf<=0 else pf/train_pf
    return trades>=g.min_test_trades and pf>=g.min_test_pf and dd<=g.max_test_dd and ratio>=g.min_train_test_ratio
