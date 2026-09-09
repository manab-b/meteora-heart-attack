from __future__ import annotations
from dataclasses import dataclass
from app.metrics.bin_drain import BinDrainSignal
from app.paper.range_state import RangeState

@dataclass(frozen=True)
class DlmmSignal:
    entry:bool
    exit:bool
    score:float
    reasons:tuple[str,...]

def evaluate(range_state:RangeState, drain:BinDrainSignal|None, fee_velocity_sol_min:float,
             min_fee_velocity:float=0.0, max_drain:float=0.95)->DlmmSignal:
    reasons=[]
    score=0.0
    if range_state.in_range:
        score+=0.35; reasons.append("in_range")
    if fee_velocity_sol_min>=min_fee_velocity:
        score+=0.35; reasons.append("fee_velocity")
    if drain is not None:
        score+=0.30*drain.score
        if drain.score>0: reasons.append("bin_drain")
    exit_signal=(not range_state.in_range or
                 (drain is not None and drain.depletion_ratio>=max_drain))
    return DlmmSignal(entry=(score>=0.7 and not exit_signal),exit=exit_signal,score=score,reasons=tuple(reasons))
