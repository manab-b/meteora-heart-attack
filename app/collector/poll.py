from __future__ import annotations
import time
from collections.abc import Callable

class PollLoop:
    def __init__(self, interval_seconds: float = 30.0):
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        self.interval_seconds = interval_seconds

    def run(self, collect: Callable[[], None], stop: Callable[[], bool]) -> None:
        while not stop():
            started = time.monotonic()
            collect()
            remaining = self.interval_seconds - (time.monotonic() - started)
            if remaining > 0:
                time.sleep(remaining)
