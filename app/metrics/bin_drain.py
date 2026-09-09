from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class BinDrainSignal:
    pool_address: str
    bin_id: int
    previous_active_bin_id: int
    current_active_bin_id: int
    previous_liquidity_raw: int
    current_liquidity_raw: int
    elapsed_seconds: float

    @property
    def active_bin_moved(self) -> bool:
        return self.previous_active_bin_id != self.current_active_bin_id

    @property
    def depletion_ratio(self) -> float:
        if self.previous_liquidity_raw <= 0:
            return 0.0
        return max(
            0.0,
            min(
                1.0,
                (self.previous_liquidity_raw - self.current_liquidity_raw)
                / self.previous_liquidity_raw,
            ),
        )

    @property
    def score(self) -> float:
        # Bin depletion during active-bin migration is deliberately discounted.
        score = self.depletion_ratio
        if self.active_bin_moved:
            score *= 0.35
        return score


def classify_bin_drain(
    *,
    pool_address: str,
    bin_id: int,
    previous_active_bin_id: int,
    current_active_bin_id: int,
    previous_x_raw: int,
    previous_y_raw: int,
    current_x_raw: int,
    current_y_raw: int,
    elapsed_seconds: float,
) -> BinDrainSignal:
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be positive")
    previous = max(0, previous_x_raw) + max(0, previous_y_raw)
    current = max(0, current_x_raw) + max(0, current_y_raw)
    return BinDrainSignal(
        pool_address,
        bin_id,
        previous_active_bin_id,
        current_active_bin_id,
        previous,
        current,
        elapsed_seconds,
    )
