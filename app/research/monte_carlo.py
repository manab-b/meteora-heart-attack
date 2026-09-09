from __future__ import annotations
import random
from dataclasses import dataclass
@dataclass(frozen=True)
class MonteCarloSummary:
    runs:int; p05:float; median:float; p95:float; loss_probability:float
def simulate(pnls:list[float],runs:int=10000,seed:int=42)->MonteCarloSummary:
    if not pnls: raise ValueError("pnls cannot be empty")
    if runs<100: raise ValueError("runs must be >= 100")
    rng=random.Random(seed); finals=[]
    for _ in range(runs): finals.append(sum(rng.choice(pnls) for _ in pnls))
    finals.sort()
    def q(p): return finals[min(len(finals)-1,max(0,int((len(finals)-1)*p)))]
    return MonteCarloSummary(runs,q(.05),q(.50),q(.95),sum(x<0 for x in finals)/runs)
