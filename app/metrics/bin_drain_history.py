from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

from app.metrics.bin_drain import classify_bin_drain


@dataclass(frozen=True)
class BinLiquidityPoint:
    pool_address: str
    bin_id: int
    active_bin_id: int
    x_amount_raw: int
    y_amount_raw: int
    observed_at: float


@dataclass(frozen=True)
class BinDrainEvent:
    pool_address: str
    bin_id: int
    previous_observed_at: float
    observed_at: float
    elapsed_seconds: float
    active_bin_moved: bool
    depletion_ratio: float
    score: float


def compare_bin_snapshots(previous: BinLiquidityPoint, current: BinLiquidityPoint) -> BinDrainEvent:
    if previous.pool_address != current.pool_address:
        raise ValueError("pool_address must match")
    if previous.bin_id != current.bin_id:
        raise ValueError("bin_id must match")
    elapsed = current.observed_at - previous.observed_at
    signal = classify_bin_drain(
        pool_address=current.pool_address,
        bin_id=current.bin_id,
        previous_active_bin_id=previous.active_bin_id,
        current_active_bin_id=current.active_bin_id,
        previous_x_raw=previous.x_amount_raw,
        previous_y_raw=previous.y_amount_raw,
        current_x_raw=current.x_amount_raw,
        current_y_raw=current.y_amount_raw,
        elapsed_seconds=elapsed,
    )
    return BinDrainEvent(
        pool_address=current.pool_address,
        bin_id=current.bin_id,
        previous_observed_at=previous.observed_at,
        observed_at=current.observed_at,
        elapsed_seconds=elapsed,
        active_bin_moved=signal.active_bin_moved,
        depletion_ratio=signal.depletion_ratio,
        score=signal.score,
    )


def compare_history(points: Iterable[BinLiquidityPoint]) -> list[BinDrainEvent]:
    grouped: dict[tuple[str, int], list[BinLiquidityPoint]] = {}
    for point in points:
        grouped.setdefault((point.pool_address, point.bin_id), []).append(point)

    events: list[BinDrainEvent] = []
    for history in grouped.values():
        history.sort(key=lambda item: item.observed_at)
        for previous, current in zip(history, history[1:]):
            if current.observed_at <= previous.observed_at:
                continue
            events.append(compare_bin_snapshots(previous, current))
    return sorted(events, key=lambda event: (event.observed_at, event.pool_address, event.bin_id))
