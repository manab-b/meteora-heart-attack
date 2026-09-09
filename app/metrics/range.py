from __future__ import annotations

def range_from_price(price: float, bin_step_bps: int, num_bins: int) -> tuple[float, float]:
    if price <= 0 or num_bins < 1 or num_bins > 10:
        raise ValueError("invalid price or bin count")
    f = 1.0 + bin_step_bps / 10000.0
    half = (num_bins - 1) / 2
    return price * (f ** -half), price * (f ** half)
