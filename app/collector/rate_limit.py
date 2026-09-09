from __future__ import annotations
import time

class RateLimiter:
    def __init__(self, requests_per_second: float = 20.0):
        if requests_per_second <= 0:
            raise ValueError("requests_per_second must be positive")
        self.interval = 1.0 / requests_per_second
        self.next_allowed = 0.0

    def wait(self) -> None:
        now = time.monotonic()
        if now < self.next_allowed:
            time.sleep(self.next_allowed - now)
        self.next_allowed = max(now, self.next_allowed) + self.interval
