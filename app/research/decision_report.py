from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class Decision:
    strategy_key:str
    status:str
    reason:str

def decide(candidate,min_test_trades=20,min_test_pf=1.1,max_loss_probability=.25):
    test=candidate.test; mc=candidate.monte_carlo
    if not candidate.robust: return Decision(candidate.config.key,"REJECT","robustness_gate")
    if int(test.get("trades",0))<min_test_trades: return Decision(candidate.config.key,"REJECT","insufficient_test_trades")
    if float(test.get("profit_factor",0))<min_test_pf: return Decision(candidate.config.key,"REJECT","test_pf_below_threshold")
    if mc is not None and mc.loss_probability>max_loss_probability: return Decision(candidate.config.key,"REJECT","monte_carlo_loss_probability")
    return Decision(candidate.config.key,"PAPER_LIVE","all_gates_passed")
