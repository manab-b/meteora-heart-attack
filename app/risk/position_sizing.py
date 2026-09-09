from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PositionSizing:
    deposit_sol: float
    max_loss_sol: float
    risk_fraction: float

def size_from_risk(capital_sol: float, risk_fraction: float, stop_loss_fraction: float) -> PositionSizing:
    if capital_sol <= 0 or not 0 < risk_fraction <= 1 or not 0 < stop_loss_fraction <= 1:
        raise ValueError("invalid risk parameters")
    max_loss=capital_sol*risk_fraction
    deposit=max_loss/stop_loss_fraction
    return PositionSizing(deposit, max_loss, risk_fraction)
