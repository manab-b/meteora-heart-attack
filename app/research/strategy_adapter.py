from __future__ import annotations
from typing import Any, Callable

class StrategyAdapter:
    def __init__(self, entry_signal: Callable[[Any,Any],bool], exit_signal: Callable[[Any,Any],bool]):
        self.entry_signal=entry_signal
        self.exit_signal=exit_signal

    def should_enter(self, tick, state): return self.entry_signal(tick,state)
    def should_exit(self, tick, state): return self.exit_signal(tick,state)
