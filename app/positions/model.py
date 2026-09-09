from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PositionSnapshot:
    position_address: str
    owner: str
    pool_address: str
    lower_bin_id: int | None
    upper_bin_id: int | None
    deposited_x: str
    deposited_y: str
    unclaimed_fee_x: str
    unclaimed_fee_y: str
    observed_at: str
    source: str

    @property
    def unclaimed_fee_x_float(self) -> float:
        return float(self.unclaimed_fee_x)

    @property
    def unclaimed_fee_y_float(self) -> float:
        return float(self.unclaimed_fee_y)
