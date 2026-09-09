from __future__ import annotations
import time
from app.runtime.health import Health
class ServiceLoop:
    def __init__(self,cycle,interval_seconds:int=30):
        if interval_seconds<=0: raise ValueError("interval_seconds must be positive")
        self.cycle=cycle; self.interval=interval_seconds; self.health=Health(time.time()); self.running=True
    def stop(self): self.running=False
    def run(self):
        while self.running:
            started=time.monotonic()
            try: self.health.success(int(self.cycle() or 0))
            except Exception: self.health.error()
            time.sleep(max(0.0,self.interval-(time.monotonic()-started)))
