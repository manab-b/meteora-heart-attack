from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class DataGate:
    min_observations:int=200
    min_trades:int=50
    max_gap_seconds:float=180.0

@dataclass(frozen=True)
class DataQuality:
    observations:int
    trades:int
    max_gap_seconds:float

    def passes(self,g:DataGate)->bool:
        return (self.observations>=g.min_observations and self.trades>=g.min_trades
                and self.max_gap_seconds<=g.max_gap_seconds)

def assess(timestamps:list[float],trades:int)->DataQuality:
    ts=sorted(timestamps)
    gap=max((b-a for a,b in zip(ts,ts[1:])),default=0.0)
    return DataQuality(len(ts),trades,gap)
