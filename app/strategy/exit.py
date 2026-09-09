from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class ExitConfig:
    out_of_range_seconds: int = 20
    max_drain_score: float = 0.70
    fee_velocity_floor_sol_min: float = 0.001

def should_exit(in_range: bool, out_of_range_seconds: float,
                drain_score: float, fee_velocity_sol_min: float,
                cfg: ExitConfig = ExitConfig()) -> tuple[bool, str]:
    if drain_score >= cfg.max_drain_score:
        return True, "LIQUIDITY_DRAIN"
    if not in_range and out_of_range_seconds >= cfg.out_of_range_seconds:
        return True, "OUT_OF_RANGE"
    if fee_velocity_sol_min < cfg.fee_velocity_floor_sol_min:
        return True, "FEE_DECAY"
    return False, ""
