from __future__ import annotations
from dataclasses import dataclass
from app.research.batch_runner import run_batch
from app.research.monte_carlo import simulate
@dataclass(frozen=True)
class ExperimentResult:
    batch:tuple
    monte_carlo:dict
def run_experiment(strategy_pnls,configs=None):
    batch=run_batch(strategy_pnls,configs)
    robust=[x for x in batch if x.robust]
    mc={x.strategy.key:simulate(strategy_pnls[x.strategy.key]) for x in robust if strategy_pnls.get(x.strategy.key)}
    return ExperimentResult(tuple(batch),mc)
