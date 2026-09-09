from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class PaperLiveGuard:
    max_open_positions:int=1
    max_daily_loss_sol:float=1.0
    max_position_loss_sol:float=.25
def can_enter(open_positions:int,daily_pnl_sol:float,guard:PaperLiveGuard=PaperLiveGuard()):
    return open_positions<guard.max_open_positions and daily_pnl_sol>-guard.max_daily_loss_sol
def can_continue(position_pnl_sol:float,guard:PaperLiveGuard=PaperLiveGuard()):
    return position_pnl_sol>-guard.max_position_loss_sol
