from __future__ import annotations
from dataclasses import dataclass
from app.research.strategy_grid import StrategyConfig,build_grid
from app.research.grid_runner import StrategyResult,evaluate
from app.research.walk_forward import run
from app.research.robust_gate import passes
from app.research.monte_carlo import simulate

@dataclass(frozen=True)
class ReplayCandidate:
    config:StrategyConfig
    train:dict
    test:dict
    robust:bool
    monte_carlo:object|None

def run_replay_grid(strategy_pnls:dict[str,list[float]],configs=None,train_ratio=.7):
    configs=configs or build_grid()
    rows=[]
    for c in configs:
        pnls=strategy_pnls.get(c.key,[])
        wf=run(c,pnls,train_ratio)
        robust=passes(wf.train,wf.test)
        mc=simulate(pnls) if robust and pnls else None
        rows.append(ReplayCandidate(c,wf.train,wf.test,robust,mc))
    return sorted(rows,key=lambda x:(x.robust,x.monte_carlo.loss_probability if x.monte_carlo else 1,
                                     x.test.get("profit_factor",0),x.test.get("net_pnl",0),
                                     -x.test.get("max_drawdown",0)),reverse=True)
