from __future__ import annotations
from dataclasses import dataclass
from app.research.strategy_grid import StrategyConfig,build_grid
from app.research.grid_runner import StrategyResult,evaluate,rank_results
from app.research.walk_forward import run
from app.research.robust_gate import passes

@dataclass(frozen=True)
class BatchResult:
    strategy:StrategyConfig
    train:dict[str,float]
    test:dict[str,float]
    robust:bool

def run_batch(strategy_pnls:dict[str,list[float]],configs=None,train_ratio:float=0.7)->list[BatchResult]:
    configs=configs or build_grid()
    out=[]
    for c in configs:
        pnls=strategy_pnls.get(c.key,[])
        wf=run(c,pnls,train_ratio)
        out.append(BatchResult(c,wf.train,wf.test,passes(wf.train,wf.test)))
    return sorted(out,key=lambda x:(x.robust,x.test.get("profit_factor",0),x.test.get("net_pnl",0),-x.test.get("max_drawdown",0)),reverse=True)
