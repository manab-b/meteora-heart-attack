from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


@dataclass(frozen=True)
class PoolDrainSummary:
    pool_address: str
    score: float
    max_bin_score: float
    mean_top_bin_score: float
    event_count: int
    active_bin_migration_events: int


def aggregate_pool_drain(
    pool_address: str,
    events: Iterable[object],
    *,
    top_n: int = 5,
) -> PoolDrainSummary:
    if top_n <= 0:
        raise ValueError("top_n must be positive")
    scores: list[float] = []
    migrations = 0
    for event in events:
        if getattr(event, "pool_address") != pool_address:
            continue
        scores.append(max(0.0, min(1.0, float(getattr(event, "score")))))
        if bool(getattr(event, "active_bin_moved")):
            migrations += 1
    if not scores:
        return PoolDrainSummary(pool_address, 0.0, 0.0, 0.0, 0, 0)
    strongest = sorted(scores, reverse=True)[:top_n]
    mean_top = round(sum(strongest) / len(strongest), 12)
    return PoolDrainSummary(
        pool_address=pool_address,
        score=mean_top,
        max_bin_score=max(scores),
        mean_top_bin_score=mean_top,
        event_count=len(scores),
        active_bin_migration_events=migrations,
    )
