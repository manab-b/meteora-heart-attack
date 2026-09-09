from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class Selection:
    strategy_key: str
    score: float
    consistency: float
    accepted: bool
    reason: str

def select(strategy_key: str, score: float, consistency: float,
           min_score: float = 0.0, min_consistency: float = 0.60) -> Selection:
    if consistency < min_consistency:
        return Selection(strategy_key,score,consistency,False,"LOW_CONSISTENCY")
    if score < min_score:
        return Selection(strategy_key,score,consistency,False,"LOW_SCORE")
    return Selection(strategy_key,score,consistency,True,"ROBUST")
