from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PositionRangeState:
    active_bin_id: int
    lower_bin_id: int
    upper_bin_id: int

    @property
    def in_range(self) -> bool:
        return self.lower_bin_id <= self.active_bin_id <= self.upper_bin_id


def range_state(active_bin_id: int, lower_bin_id: int, upper_bin_id: int) -> PositionRangeState:
    if lower_bin_id > upper_bin_id:
        raise ValueError("lower_bin_id must not exceed upper_bin_id")
    return PositionRangeState(active_bin_id, lower_bin_id, upper_bin_id)


def consecutive_range_survival(
    previous_seconds: float,
    elapsed_seconds: float,
    active_bin_id: int,
    lower_bin_id: int,
    upper_bin_id: int,
) -> float:
    if previous_seconds < 0 or elapsed_seconds < 0:
        raise ValueError("survival times must be non-negative")
    state = range_state(active_bin_id, lower_bin_id, upper_bin_id)
    return previous_seconds + elapsed_seconds if state.in_range else 0.0


def raw_fee_delta(previous_raw: int | str, current_raw: int | str) -> tuple[int, bool]:
    previous = int(previous_raw)
    current = int(current_raw)
    if previous < 0 or current < 0:
        raise ValueError("fee observations must be non-negative")
    delta = current - previous
    return max(0, delta), delta < 0


def position_fee_delta(
    previous_fee_x_raw: int | str,
    previous_fee_y_raw: int | str,
    current_fee_x_raw: int | str,
    current_fee_y_raw: int | str,
) -> tuple[int, int, bool]:
    dx, reset_x = raw_fee_delta(previous_fee_x_raw, current_fee_x_raw)
    dy, reset_y = raw_fee_delta(previous_fee_y_raw, current_fee_y_raw)
    return dx, dy, reset_x or reset_y
