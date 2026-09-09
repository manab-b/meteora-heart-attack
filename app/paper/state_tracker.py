from __future__ import annotations
from dataclasses import dataclass
from app.meteora.market_state import Tick

@dataclass
class State:
    last_at:float=0.0
    last_price:float=0.0
    out_of_range_since:float|None=None
    volume_usd:float=0.0
    fee_usd:float=0.0
    liquidity_usd:float=0.0
    rug_flags:tuple[str,...]=()

    @property
    def out_of_range_seconds(self):
        return 0.0 if self.out_of_range_since is None else max(0.0,self.last_at-self.out_of_range_since)

class StateTracker:
    def update(self,tick:Tick)->State:
        if not tick.in_range:
            self.state.out_of_range_since=self.state.out_of_range_since or tick.observed_at
        else: self.state.out_of_range_since=None
        self.state.last_at=tick.observed_at; self.state.last_price=tick.price
        self.state.volume_usd=tick.volume_usd; self.state.fee_usd=tick.fee_usd
        self.state.liquidity_usd=tick.liquidity_usd; self.state.rug_flags=tick.rug_flags
        return self.state
    def __init__(self): self.state=State()
