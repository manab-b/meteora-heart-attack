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
    return (current.unclaimed_sol - previous.unclaimed_sol) / dt

def fee_velocity_per_minute(previous: FeeObservation, current: FeeObservation) -> float:
    return fee_velocity(previous, current) * 60.0
