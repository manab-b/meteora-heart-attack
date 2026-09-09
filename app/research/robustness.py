from __future__ import annotations
from dataclasses import dataclass
import statistics

@dataclass(frozen=True)
class Robustness:
    samples: int
    mean: float
    stdev: float
    consistency: float

def assess(scores: list[float]) -> Robustness:
    if not scores: return Robustness(0,0,0,0)
    mean=statistics.fmean(scores)
    stdev=statistics.stdev(scores) if len(scores)>1 else 0.0
    consistency=sum(x>0 for x in scores)/len(scores)
    return Robustness(len(scores),mean,stdev,consistency)
