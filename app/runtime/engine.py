from __future__ import annotations
from dataclasses import dataclass
@dataclass(frozen=True)
class EngineCycleResult:
    pools:int; observations:int; trades_closed:int; errors:int
class PaperEngine:
    def __init__(self,pools,process_pool):
        self.pools=pools; self.process_pool=process_pool
    def run_cycle(self)->EngineCycleResult:
        observations=closed=errors=0
        for pool in self.pools:
            try:
                results=self.process_pool(pool)
                observations+=len(results)
                closed+=sum(x is not None and isinstance(x,dict) and "net_pnl_sol" in x for x in results)
            except Exception:
                errors+=1
        return EngineCycleResult(len(self.pools),observations,closed,errors)
