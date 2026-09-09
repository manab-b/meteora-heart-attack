from __future__ import annotations
import math
from dataclasses import dataclass
import random

@dataclass(frozen=True)
class DrawdownStats:
    max_drawdown: float
    p95_drawdown: float
    loss_probability: float

def equity_drawdown(values: list[float]) -> float:
    peak=float("-inf"); max_dd=0.0
    for v in values:
        peak=max(peak,v)
        if peak != 0: max_dd=max(max_dd,(peak-v)/abs(peak))
    return max_dd

def bootstrap_fee_paths(fees: list[float], *, iterations: int=10_000, seed: int=42) -> DrawdownStats:
    if not fees or iterations < 1: return DrawdownStats(0.0,0.0,0.0)
    rng=random.Random(seed); dds=[]; losses=0
    for _ in range(iterations):
        path=[0.0]
        for _ in fees: path.append(path[-1]+rng.choice(fees))
        dds.append(equity_drawdown(path))
        if path[-1] < 0: losses += 1
    dds.sort()
    idx=min(len(dds)-1, math.ceil(0.95*len(dds))-1)
    return DrawdownStats(dds[idx], dds[idx], losses/iterations)
