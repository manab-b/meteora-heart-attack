from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class FeeObservation:
    timestamp: float
    unclaimed_sol: float


def fee_velocity(previous: FeeObservation, current: FeeObservation) -> float:
    dt = current.timestamp - previous.timestamp
    if dt <= 0:
        raise ValueError("timestamps must increase")
    if previous.unclaimed_sol < 0 or current.unclaimed_sol < 0:
        raise ValueError("fees must be non-negative")
    return max(0.0, current.unclaimed_sol - previous.unclaimed_sol) / dt


def fee_velocity_per_minute(previous: FeeObservation, current: FeeObservation) -> float:
    return fee_velocity(previous, current) * 60.0
