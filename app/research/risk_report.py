from __future__ import annotations
from dataclasses import dataclass
import random, math

@dataclass(frozen=True)
class RiskReport:
    observations: int
    mean_return: float
    median_return: float
    win_rate: float
    max_drawdown: float
    p05_terminal: float
    p50_terminal: float
    p95_terminal: float
    loss_probability: float

def summarize_returns(returns: list[float], iterations: int = 10_000, seed: int = 42) -> RiskReport:
    if not returns:
        return RiskReport(0,0,0,0,0,0,0,0,0)
    vals=sorted(float(x) for x in returns)
    win=sum(x>0 for x in vals)/len(vals)
    eq=peak=0.0; dd=0.0
    for x in returns:
        eq += x; peak=max(peak,eq); dd=max(dd,peak-eq)
    rng=random.Random(seed); terminals=[]
    for _ in range(iterations):
        total=0.0
        for _ in returns: total += rng.choice(returns)
        terminals.append(total)
    terminals.sort()
    def q(p):
        return terminals[min(len(terminals)-1, max(0, math.ceil(p*len(terminals))-1))]
    return RiskReport(len(vals), sum(vals)/len(vals), q(.5), win, dd, q(.05), q(.5), q(.95),
                      sum(x<0 for x in terminals)/len(terminals))
