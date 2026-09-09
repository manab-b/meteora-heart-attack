from __future__ import annotations
from app.runtime.observation_adapter import adapt
from app.runtime.e2e_cycle import evaluate_observation
from app.runtime.paper_ledger import PaperTrade
class E2ERunner:
    def __init__(self,ledger,size_sol=1.0): self.ledger=ledger; self.size_sol=size_sol
    def process(self,raw,strategy_key,now):
        obs=adapt(raw,strategy_key)
        d=evaluate_observation(raw,strategy_key)
        trade_id=f"{obs.pool_address}:{strategy_key}"
        if d.entry and trade_id not in self.ledger.open:
            self.ledger.enter(PaperTrade(trade_id,strategy_key,obs.pool_address,now,obs.price,self.size_sol))
            return "ENTRY"
        if d.exit and trade_id in self.ledger.open:
            self.ledger.exit(trade_id,now,obs.price,d.reason)
            return "EXIT"
        return "HOLD" if trade_id in self.ledger.open else "WAIT"
