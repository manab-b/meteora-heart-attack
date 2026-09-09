from __future__ import annotations
from dataclasses import dataclass
from app.runtime.paper_ledger import PaperLedger,PaperTrade
from app.runtime.paper_live_guard import can_enter,can_continue
@dataclass(frozen=True)
class LiveCycleResult:
    action:str; trade_id:str|None; reason:str
class PaperLiveCycle:
    def __init__(self,ledger:PaperLedger,guard=None): self.ledger=ledger; self.guard=guard
    def handle(self,signal,trade_id,pool_address,now,price,size_sol):
        open_count=len(self.ledger.open); daily=self.ledger.daily_pnl(now-86400,now)
        if signal.exit and trade_id in self.ledger.open:
            c=self.ledger.exit(trade_id,now,price,"signal_exit"); return LiveCycleResult("EXIT",trade_id,c.reason)
        if signal.entry and can_enter(open_count,daily,self.guard or __import__("app.runtime.paper_live_guard",fromlist=["PaperLiveGuard"]).PaperLiveGuard()):
            self.ledger.enter(PaperTrade(trade_id,signal.strategy_key,pool_address,now,price,size_sol))
            return LiveCycleResult("ENTRY",trade_id,"entry_signal")
        return LiveCycleResult("HOLD" if trade_id in self.ledger.open else "WAIT",trade_id,None)
