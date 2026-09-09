from __future__ import annotations
from dataclasses import dataclass
from app.research.monte_carlo import MonteCarloSummary
@dataclass(frozen=True)
class FinalCandidate:
    strategy_key:str; test_pf:float; test_pnl:float; test_dd:float; mc:MonteCarloSummary
def select(rows:list[FinalCandidate],max_loss_probability:float=0.25)->list[FinalCandidate]:
    return sorted((r for r in rows if r.mc.loss_probability<=max_loss_probability),
                  key=lambda r:(r.test_pf,r.test_pnl,-r.test_dd,r.mc.median),reverse=True)
