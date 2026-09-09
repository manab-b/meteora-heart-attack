from __future__ import annotations
from dataclasses import dataclass
from app.paper.dlmm_signal import evaluate

@dataclass(frozen=True)
class Evaluation:
    action:str
    score:float
    reasons:tuple[str,...]

def evaluate_tick(range_state,drain,fee_velocity_sol_min,position_open,
                  min_fee_velocity=0.0,max_drain=0.95)->Evaluation:
    s=evaluate(range_state,drain,fee_velocity_sol_min,min_fee_velocity,max_drain)
    if position_open: return Evaluation("EXIT" if s.exit else "HOLD",s.score,s.reasons)
    return Evaluation("ENTRY" if s.entry else "WAIT",s.score,s.reasons)
