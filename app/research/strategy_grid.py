from __future__ import annotations
from dataclasses import dataclass
from itertools import product

@dataclass(frozen=True)
class StrategyConfig:
    bin_step_bps: int
    num_bins: int
    min_score: float
    max_drain: float

def grid(bin_steps=(10,25,50), num_bins=(3,5,7), min_scores=(0.60,0.70), max_drains=(0.45,0.55)):
    return [StrategyConfig(*x) for x in product(bin_steps,num_bins,min_scores,max_drains)]
