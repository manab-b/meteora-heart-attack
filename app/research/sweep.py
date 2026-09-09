from __future__ import annotations
from dataclasses import dataclass
from itertools import product
from app.strategy.backtest import Observation, StrategyBacktest
from app.strategy.entry import EntryConfig
from app.strategy.exit import ExitConfig
from app.reporting.report import build_report

@dataclass(frozen=True)
class SweepConfig:
    bins: int
    min_volume_usd: float
    min_fee_velocity_sol_min: float
    max_drain_score: float
    min_range_survival_seconds: float
    out_of_range_seconds: int
    fee_velocity_floor_sol_min: float

def run_sweep(observations_by_bins: dict[int, list[Observation]],
              bins_values: tuple[int,...] = (3,5,7,9),
              volume_values: tuple[float,...] = (50_000,100_000,250_000),
              fee_values: tuple[float,...] = (0.005,0.01,0.02),
              drain_values: tuple[float,...] = (0.25,0.35,0.50),
              survival_values: tuple[float,...] = (30,60,120),
              oor_values: tuple[int,...] = (10,20,30),
              floor_values: tuple[float,...] = (0.0005,0.001,0.002)) -> list[dict]:
    results = []
    for bins, vol, fee, drain, survival, oor, floor in product(
        bins_values, volume_values, fee_values, drain_values,
        survival_values, oor_values, floor_values
    ):
        obs = observations_by_bins.get(bins, [])
        if not obs:
            continue
        bt = StrategyBacktest(
            EntryConfig(vol, fee, drain, survival),
            ExitConfig(oor, max(0.5, drain + 0.35), floor),
        )
        trades = bt.run(obs, fee_per_minute_to_sol=fee)
        report = build_report(trades)
        results.append({
            "bins": bins, "min_volume_usd": vol,
            "min_fee_velocity_sol_min": fee,
            "max_drain_score": drain,
            "min_range_survival_seconds": survival,
            "out_of_range_seconds": oor,
            "fee_velocity_floor_sol_min": floor,
            **report,
        })
    return results
