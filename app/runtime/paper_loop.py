from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class PaperLoopConfig:
    interval_seconds:int=30

class PaperLoop:
    def __init__(self, fetch_watchlist:Callable[[],list[str]],
                 observe:Callable[[str],object], process:Callable[[str,object],None],
                 config:PaperLoopConfig=PaperLoopConfig()):
        self.fetch_watchlist=fetch_watchlist; self.observe=observe; self.process=process; self.config=config

    def run_once(self)->int:
        n=0
        for pool in self.fetch_watchlist():
            self.process(pool,self.observe(pool)); n+=1
        return n

    def run_forever(self, stop:Callable[[],bool]=lambda:False):
        while not stop():
            started=time.monotonic()
            self.run_once()
            time.sleep(max(0,self.config.interval_seconds-(time.monotonic()-started)))
