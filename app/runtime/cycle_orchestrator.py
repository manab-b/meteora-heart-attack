from __future__ import annotations
from dataclasses import dataclass
from app.runtime.paper_ledger import PaperLedger
from app.runtime.live_cycle import PaperLiveCycle
@dataclass(frozen=True)
class OrchestratorResult:
    observations:int; actions:int; errors:int
class CycleOrchestrator:
    def __init__(self,pool_provider,signal_provider,ledger=None,guard=None):
        self.pool_provider=pool_provider; self.signal_provider=signal_provider
        self.ledger=ledger or PaperLedger(); self.live=PaperLiveCycle(self.ledger,guard)
    def run_once(self,now,price_provider,size_sol=1.0):
        observations=actions=errors=0
        for pool in self.pool_provider():
            observations+=1
            try:
                signal,trade_id,price=self.signal_provider(pool)
                if signal is None: continue
                r=self.live.handle(signal,trade_id,pool.address,now,price,size_sol)
                actions+=r.action!="WAIT"
            except Exception:
                errors+=1
        return OrchestratorResult(observations,actions,errors)
