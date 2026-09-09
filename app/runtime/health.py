from __future__ import annotations
from dataclasses import dataclass
import time

@dataclass
class RuntimeHealth:
    cycles: int = 0
    failures: int = 0
    last_success_epoch: float | None = None
    last_error: str | None = None

    def success(self) -> None:
        self.cycles += 1
        self.last_success_epoch = time.time()
        self.last_error = None

    def failure(self, error: Exception) -> None:
        self.cycles += 1
        self.failures += 1
        self.last_error = f"{type(error).__name__}: {error}"

    @property
    def healthy(self) -> bool:
        return self.failures == 0 or self.last_success_epoch is not None
