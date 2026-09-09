from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable, Callable, Any

@dataclass(frozen=True)
class ReplayTick:
    observed_at: float
    pool_address: str
    payload: dict[str, Any]

class ReplayEngine:
    def __init__(self, ticks: Iterable[ReplayTick]):
        self.ticks=sorted(ticks,key=lambda x:x.observed_at)

    def run(self, on_tick: Callable[[ReplayTick], None]) -> int:
        for tick in self.ticks: on_tick(tick)
        return len(self.ticks)
