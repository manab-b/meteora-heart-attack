from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeeVelocity:
    """Fee-rate observation derived from cumulative/position fee deltas.

    `fee_delta_sol` must come from position-level fee observations. Pool-wide
    rolling fee fields are intentionally not accepted here.
    """

    fee_delta_sol: float
    elapsed_seconds: float

    @property
    def sol_per_minute(self) -> float:
        if self.elapsed_seconds <= 0:
            return 0.0
        return self.fee_delta_sol / self.elapsed_seconds * 60.0


def fee_velocity_sol_min(fee_delta_sol: float, elapsed_seconds: float) -> float:
    if elapsed_seconds <= 0:
        return 0.0
    return fee_delta_sol / elapsed_seconds * 60.0
