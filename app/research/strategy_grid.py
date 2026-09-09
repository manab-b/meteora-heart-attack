from __future__ import annotations
from dataclasses import dataclass
from itertools import product
@dataclass(frozen=True)
class StrategyConfig:
    key:str; min_score:float; min_fee_velocity:float; max_drain:float; max_out_seconds:int
def build_grid(scores=(0.7,0.8,0.9),fees=(0.0,0.01,0.05),drains=(0.8,0.9,0.95),timeouts=(30,60,120)):
    return [StrategyConfig(f"S{i:03d}",s,f,d,t) for i,(s,f,d,t) in enumerate(product(scores,fees,drains,timeouts),1)]
