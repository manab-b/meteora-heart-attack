from __future__ import annotations

from dataclasses import dataclass


@dataclass
class HealthCheckpoint:
    cycles: int = 0
    errors: int = 0
    last_success_at: float = 0.0
    healthy: bool = True

    def success(self, timestamp: float) -> None:
        self.cycles += 1
        self.last_success_at = timestamp
        self.healthy = True

    def failure(self, _error: Exception | None = None) -> None:
        self.cycles += 1
        self.errors += 1
        self.healthy = False
