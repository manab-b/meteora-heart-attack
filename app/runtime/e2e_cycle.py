from __future__ import annotations
from dataclasses import dataclass
from app.runtime.score_engine import score_state,eligible_state
@dataclass(frozen=True)
class CycleDecision:
    strategy_key:str; score:float; entry:bool; exit:bool; reason:str
def evaluate_observation(state,strategy_key,entry_threshold=1.0,exit_threshold=0.0):
    score=score_state(drain_score=float(state["drain_score"]),fee_velocity=float(state["fee_velocity"]),range_survival=float(state["range_survival"]))["score"]
    eligible=eligible_state(score=score,min_score=entry_threshold,range_survival=float(state["range_survival"]),fee_velocity=float(state["fee_velocity"]))
    exit_signal=score<=exit_threshold or float(state["range_survival"])<=0
    reason="entry_threshold" if eligible else ("range_exit" if exit_signal else "below_threshold")
    return CycleDecision(strategy_key,score,eligible,exit_signal,reason)
