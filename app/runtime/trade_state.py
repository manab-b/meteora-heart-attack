from __future__ import annotations
from dataclasses import dataclass
@dataclass
class PositionState:
    trade_id:str
    entry_price:float
    entry_at:float
    strategy_key:str
    pool_address:str
    size_sol:float
    def mark(self,price:float)->float:
        return (price-self.entry_price)*self.size_sol/self.entry_price
