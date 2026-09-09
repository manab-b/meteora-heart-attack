from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BinLiquiditySnapshot:
    bin_id: int
    x_amount_raw: int
    y_amount_raw: int
    observed_at: float

    @property
    def total_raw(self) -> int:
        return self.x_amount_raw + self.y_amount_raw


def liquidity_change_ratio(previous: BinLiquiditySnapshot, current: BinLiquiditySnapshot) -> float:
    """Return fractional liquidity depletion between two observations.

    This is deliberately a raw-token liquidity signal. It must not be treated
    as USD TVL unless both token amounts have been independently valued.
    """
    if previous.bin_id != current.bin_id:
        raise ValueError("snapshots must reference the same bin")
    if previous.total_raw <= 0:
        return 0.0
    drop = previous.total_raw - current.total_raw
    return max(0.0, min(1.0, drop / previous.total_raw))


def bin_removed(previous: BinLiquiditySnapshot, current: BinLiquiditySnapshot) -> bool:
    return previous.total_raw > 0 and current.total_raw == 0
