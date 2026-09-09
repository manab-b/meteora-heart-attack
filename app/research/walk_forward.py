from __future__ import annotations
from dataclasses import dataclass
from app.research.grid_runner import evaluate
@dataclass(frozen=True)
class WalkForwardResult:
    strategy_key:str; train:dict[str,float]; test:dict[str,float]
def run(config,pnls:list[float],train_ratio:float=0.7):
    if not 0.5<=train_ratio<1: raise ValueError("train_ratio must be in [0.5,1)")
    if len(pnls)<2: return WalkForwardResult(config.key,{}, {})
    cut=max(1,min(len(pnls)-1,int(len(pnls)*train_ratio)))
    return WalkForwardResult(config.key,evaluate(config,pnls[:cut]).metrics,evaluate(config,pnls[cut:]).metrics)
