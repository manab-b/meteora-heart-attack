from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class PaperTrade:
    trade_id:str; strategy_key:str; pool_address:str; entry_at:float; entry_price:float; size_sol:float
@dataclass(frozen=True)
class ClosedTrade:
    trade:PaperTrade; exit_at:float; exit_price:float; net_pnl_sol:float; reason:str
class PaperLedger:
    def __init__(self): self.open:dict[str,PaperTrade]={}; self.closed:list[ClosedTrade]=[]
    def enter(self,t:PaperTrade):
        if t.trade_id in self.open or any(x.trade.trade_id==t.trade_id for x in self.closed): return False
        self.open[t.trade_id]=t; return True
    def exit(self,trade_id,exit_at,exit_price,reason,fee_sol=0.0):
        t=self.open.pop(trade_id)
        pnl=(exit_price-t.entry_price)*t.size_sol/t.entry_price-fee_sol
        c=ClosedTrade(t,exit_at,exit_price,pnl,reason); self.closed.append(c); return c
    def daily_pnl(self,day_start,day_end):
        return sum(x.net_pnl_sol for x in self.closed if day_start<=x.exit_at<day_end)
