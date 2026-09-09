from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PaperAccounting:
    entry_value_sol: float
    claimed_fee_sol: float
    unrealized_il_sol: float
    net_pnl_sol: float

def account(entry_value_sol: float, claimed_fee_sol: float, unrealized_il_sol: float=0.0) -> PaperAccounting:
    return PaperAccounting(entry_value_sol,claimed_fee_sol,unrealized_il_sol,
                           claimed_fee_sol-unrealized_il_sol)
