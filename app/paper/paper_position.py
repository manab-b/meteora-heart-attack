from __future__ import annotations
from dataclasses import dataclass

@dataclass
class PaperPosition:
    pool_address:str
    strategy_key:str
    entry_at:float
    entry_price:float
    notional_sol:float
    fees_sol:float=0.0
    exit_at:float|None=None
    exit_price:float|None=None
    exit_reason:str|None=None

    @property
    def open(self): return self.exit_at is None

    def close(self,at:float,price:float,reason:str,fees_sol:float=0.0):
        if not self.open: raise RuntimeError("position already closed")
        self.exit_at=at; self.exit_price=price; self.exit_reason=reason; self.fees_sol+=fees_sol
