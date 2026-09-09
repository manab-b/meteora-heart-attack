from __future__ import annotations
from dataclasses import dataclass, field
from time import monotonic
from typing import Callable

@dataclass
class ResearchRuntime:
    collect: Callable[[], None]
    cycle: Callable[[], None]
    report: Callable[[], object] | None = None
    interval_seconds: int = 30
    max_iterations: int | None = None
    errors: int = 0
    iterations: int = 0
    last_error: str | None = None
    history: list[object] = field(default_factory=list)

    def run(self) -> int:
        if self.interval_seconds < 1: raise ValueError("interval_seconds must be >= 1")
        while self.max_iterations is None or self.iterations < self.max_iterations:
            started=monotonic()
            try:
                self.collect()
                self.cycle()
                if self.report is not None:
                    self.history.append(self.report())
                self.last_error=None
            except Exception as exc:
                self.errors += 1
                self.last_error=f"{type(exc).__name__}: {exc}"
            self.iterations += 1
            delay=self.interval_seconds-(monotonic()-started)
            if delay > 0 and (self.max_iterations is None or self.iterations < self.max_iterations):
                __import__("time").sleep(delay)
        return self.iterations
