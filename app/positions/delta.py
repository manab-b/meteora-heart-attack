from __future__ import annotations

from dataclasses import dataclass

from .model import PositionSnapshot


@dataclass(frozen=True)
class PositionFeeDelta:
    position_address: str
    pool_address: str
    elapsed_seconds: float
    delta_fee_x: float
    delta_fee_y: float

    @property
    def fee_x_per_minute(self) -> float:
        return round(self.delta_fee_x / self.elapsed_seconds * 60, 12) if self.elapsed_seconds > 0 else 0.0

    @property
    def fee_y_per_minute(self) -> float:
        return round(self.delta_fee_y / self.elapsed_seconds * 60, 12) if self.elapsed_seconds > 0 else 0.0


def calculate_fee_delta(previous: PositionSnapshot, current: PositionSnapshot) -> PositionFeeDelta:
    from datetime import datetime

    a = datetime.fromisoformat(previous.observed_at.replace("Z", "+00:00"))
    b = datetime.fromisoformat(current.observed_at.replace("Z", "+00:00"))
    elapsed = (b - a).total_seconds()
    if elapsed <= 0:
        raise ValueError("current snapshot must be later than previous snapshot")
    return PositionFeeDelta(
        previous.position_address,
        previous.pool_address,
        elapsed,
        current.unclaimed_fee_x_float - previous.unclaimed_fee_x_float,
        current.unclaimed_fee_y_float - previous.unclaimed_fee_y_float,
    )
