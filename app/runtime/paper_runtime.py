from __future__ import annotations
import time
from app.runtime.recovery import RuntimeCheckpoint
from app.runtime.idempotency import observation_key

class PaperRuntime:
    def __init__(self,cycle,interval_seconds=30):
        self.cycle=cycle; self.interval=interval_seconds; self.checkpoint=RuntimeCheckpoint(); self.running=False
    def run_once(self):
        try:
            result=self.cycle()
            self.checkpoint.success()
            return result
        except Exception as exc:
            self.checkpoint.failure(exc)
            return None
    def run_forever(self):
        self.running=True
        while self.running:
            started=time.monotonic()
            self.run_once()
            time.sleep(max(0,self.interval-(time.monotonic()-started)))
    def stop(self): self.running=False
