from __future__ import annotations

from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class FeeDelta:
    """Position-level fee accrual between two observations.

    A negative raw delta is retained as a reset/claim event rather than being
    misclassified as earned fees. This keeps claims and fee accrual separate.
    """

    position_address: str
    observed_at: float
    previous_fee_sol: float
    current_fee_sol: float

    @property
    def raw_delta_sol(self) -> float:
        return self.current_fee_sol - self.previous_fee_sol

    @property
    def accrued_fee_sol(self) -> float:
        return max(0.0, self.raw_delta_sol)

    @property
    def reset_or_claim(self) -> bool:
        return self.raw_delta_sol < 0.0


def fee_delta(
    position_address: str,
    previous_fee_sol: float,
    current_fee_sol: float,
    observed_at: float,
) -> FeeDelta:
    if previous_fee_sol < 0 or current_fee_sol < 0:
        raise ValueError("fee values must be non-negative")
    return FeeDelta(
        position_address=position_address,
        observed_at=observed_at,
        previous_fee_sol=previous_fee_sol,
        current_fee_sol=current_fee_sol,
    )


def fee_velocity_from_delta(delta: FeeDelta, elapsed_seconds: float) -> float:
    if elapsed_seconds <= 0:
        return 0.0
    return delta.accrued_fee_sol / elapsed_seconds * 60.0
