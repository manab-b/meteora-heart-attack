from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class Signal:
    strategy_key:str
    entry:bool
    exit:bool
    score:float
    reason:str
class HeartAttackSignalProvider:
    def __init__(self,score_fn,entry_threshold=1.0,exit_threshold=0.0):
        self.score_fn=score_fn; self.entry_threshold=entry_threshold; self.exit_threshold=exit_threshold
    def __call__(self,pool):
        state=self.score_fn(pool)
        score=float(state["score"])
        entry=bool(state.get("eligible",True) and score>=self.entry_threshold)
        exit=bool(score<=self.exit_threshold)
        return Signal(state["strategy_key"],entry,exit,score,state.get("reason","")),state.get("trade_id",f"{pool.address}:{state['strategy_key']}"),float(state["price"])
