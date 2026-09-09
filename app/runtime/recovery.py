from __future__ import annotations
import time
from dataclasses import dataclass
@dataclass
class RuntimeCheckpoint:
    last_success_at:float=0.0
    cycles:int=0
    errors:int=0
    last_error:str=""
    def success(self,now=None):
        self.last_success_at=now or time.time(); self.cycles+=1; self.last_error=""
    def failure(self,error:Exception):
        self.errors+=1; self.last_error=f"{type(error).__name__}: {error}"
    @property
    def healthy(self):
        return self.cycles>0 and not self.last_error
