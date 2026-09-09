from __future__ import annotations
from dataclasses import dataclass
import time

@dataclass
class Health:
    started_at:float
    cycles:int=0
    observations:int=0
    errors:int=0
    last_success_at:float|None=None
    def success(self,n:int):
        self.cycles+=1; self.observations+=n; self.last_success_at=time.time()
    def error(self):
        self.cycles+=1; self.errors+=1
    @property
    def error_rate(self): return self.errors/self.cycles if self.cycles else 0.0
