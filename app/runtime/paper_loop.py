from __future__ import annotations
import time
from dataclasses import dataclass
from typing import Callable

@dataclass(frozen=True)
class LoopConfig:
    interval_seconds: int = 30
    max_iterations: int | None = None

class PaperLoop:
    def __init__(self, collect: Callable[[], None], cycle: Callable[[], None], config: LoopConfig = LoopConfig()):
        if config.interval_seconds < 1: raise ValueError("interval_seconds must be >= 1")
        self.collect, self.cycle, self.config = collect, cycle, config

    def run(self) -> int:
        count = 0
        while self.config.max_iterations is None or count < self.config.max_iterations:
            started = time.monotonic()
            self.collect()
            self.cycle()
            count += 1
            remaining = self.config.interval_seconds - (time.monotonic() - started)
            if remaining > 0 and (self.config.max_iterations is None or count < self.config.max_iterations):
                time.sleep(remaining)
        return count
