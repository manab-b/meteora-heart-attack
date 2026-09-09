from __future__ import annotations
from dataclasses import dataclass
from app.metrics.range import range_from_price

@dataclass(frozen=True)
class BinConfigResult:
    num_bins: int
    min_price: float
    max_price: float

def compare_bin_counts(price: float, bin_step_bps: int,
                       counts: tuple[int, ...] = (3, 5, 7, 9)) -> list[BinConfigResult]:
    return [
        BinConfigResult(n, *range_from_price(price, bin_step_bps, n))
        for n in counts
    ]
