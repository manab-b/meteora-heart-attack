from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class GateResult:
    passed: bool
    reasons: tuple[str,...]

def gate(*, median_pnl: float, p05_pnl: float, max_drawdown: float,
         loss_probability: float, consistency: float,
         min_p05: float=0.0, max_dd: float=0.25,
         max_loss_probability: float=0.50, min_consistency: float=0.60) -> GateResult:
    reasons=[]
    if p05_pnl < min_p05: reasons.append("P05_BELOW_MIN")
    if max_drawdown > max_dd: reasons.append("DRAWDOWN_TOO_HIGH")
    if loss_probability > max_loss_probability: reasons.append("LOSS_PROBABILITY_TOO_HIGH")
    if consistency < min_consistency: reasons.append("INCONSISTENT")
    if median_pnl <= 0: reasons.append("MEDIAN_PNL_NON_POSITIVE")
    return GateResult(not reasons,tuple(reasons))
