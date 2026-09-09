from __future__ import annotations
from dataclasses import dataclass
from app.research.sweep import run_sweep

@dataclass(frozen=True)
class WalkForwardResult:
    train_rows: list[dict]
    test_rows: list[dict]
    selected: dict | None

def split_observations(observations: list, train_ratio: float = 0.7):
    if not 0 < train_ratio < 1:
        raise ValueError("train_ratio must be between 0 and 1")
    cut = max(1, min(len(observations)-1, int(len(observations)*train_ratio)))
    return observations[:cut], observations[cut:]

def run_walkforward(observations_by_bins: dict[int,list], train_ratio: float = 0.7) -> WalkForwardResult:
    train = {}
    test = {}
    for bins, observations in observations_by_bins.items():
        a,b = split_observations(observations, train_ratio)
        train[bins], test[bins] = a,b
    train_rows = run_sweep(train)
    if not train_rows:
        return WalkForwardResult([], [], None)
    selected = max(train_rows, key=lambda x: (x.get("median_fee_sol",0), x.get("total_fee_sol",0)))
    test_rows = run_sweep(test, bins_values=(selected["bins"],),
                          volume_values=(selected["min_volume_usd"],),
                          fee_values=(selected["min_fee_velocity_sol_min"],),
                          drain_values=(selected["max_drain_score"],),
                          survival_values=(selected["min_range_survival_seconds"],),
                          oor_values=(selected["out_of_range_seconds"],),
                          floor_values=(selected["fee_velocity_floor_sol_min"],))
    return WalkForwardResult(train_rows, test_rows, selected)
