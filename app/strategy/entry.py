from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class EntryConfig:
    min_volume_usd: float = 100_000
    min_fee_velocity_sol_min: float = 0.01
    max_drain_score: float = 0.35
    min_range_survival_seconds: float = 60.0

def should_enter(volume_usd: float, fee_velocity_sol_min: float,
                 drain_score: float, range_survival_seconds: float,
                 cfg: EntryConfig = EntryConfig()) -> bool:
    return (
        volume_usd >= cfg.min_volume_usd
        and fee_velocity_sol_min >= cfg.min_fee_velocity_sol_min
        and drain_score <= cfg.max_drain_score
        and range_survival_seconds >= cfg.min_range_survival_seconds
    )
