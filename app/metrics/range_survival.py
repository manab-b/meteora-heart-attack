from __future__ import annotations


def in_bin_range(price: float, lower_price: float, upper_price: float) -> bool:
    return lower_price <= price <= upper_price


def update_range_survival_seconds(
    previous_survival_seconds: float,
    elapsed_seconds: float,
    in_range: bool,
) -> float:
    """Accumulate consecutive in-range time only.

    A single out-of-range observation resets the consecutive survival clock.
    """
    if not in_range:
        return 0.0
    if elapsed_seconds < 0:
        return previous_survival_seconds
    return previous_survival_seconds + elapsed_seconds
