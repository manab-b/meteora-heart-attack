from __future__ import annotations
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class WatchlistRunnerConfig:
    interval_seconds: int=30

class WatchlistRunner:
    def __init__(self, watchlist: Callable[[],list[str]], observe: Callable[[str],object],
                 on_tick: Callable[[str,object],None], config=WatchlistRunnerConfig()):
        self.watchlist,self.observe,self.on_tick,self.config=watchlist,observe,on_tick,config

    def run_once(self) -> int:
        count=0
        for address in self.watchlist():
            self.on_tick(address,self.observe(address))
            count+=1
        return count
