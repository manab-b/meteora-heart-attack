from __future__ import annotations
from dataclasses import dataclass
import random, statistics

@dataclass(frozen=True)
class MonteCarloStats:
    runs:int
    median_final_sol:float
    p05_final_sol:float
    p95_final_sol:float
    loss_probability:float
    median_max_drawdown_sol:float

def run(trade_pnls:list[float], initial_sol:float=5.0, runs:int=10_000, seed:int=42)->MonteCarloStats:
    if not trade_pnls or runs<=0: return MonteCarloStats(runs,initial_sol,initial_sol,initial_sol,0.0,0.0)
    rng=random.Random(seed); finals=[]; dds=[]
    for _ in range(runs):
        equity=initial_sol; peak=equity; dd=0.0
        for pnl in rng.sample(trade_pnls,len(trade_pnls)):
            equity+=pnl; peak=max(peak,equity); dd=max(dd,peak-equity)
        finals.append(equity); dds.append(dd)
    finals.sort()
    q=lambda p: finals[min(len(finals)-1,int((len(finals)-1)*p))]
    return MonteCarloStats(runs,statistics.median(finals),q(.05),q(.95),
                           sum(x<initial_sol for x in finals)/runs,statistics.median(dds))
