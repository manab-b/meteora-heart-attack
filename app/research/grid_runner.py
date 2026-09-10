from __future__ import annotations

from dataclasses import dataclass

from app.paper.canonical_position import CanonicalPositionState
from app.paper.dlmm_signal import DlmmSignal, evaluate_canonical_state
from app.research.metrics import summarize
from app.research.strategy_grid import StrategyConfig


@dataclass(frozen=True)
class StrategyResult:
    config: StrategyConfig
    metrics: dict[str, float]


def evaluate(config: StrategyConfig, pnls: list[float]) -> StrategyResult:
    return StrategyResult(config, summarize(pnls))


def evaluate_signal(
    config: StrategyConfig,
    state: CanonicalPositionState,
    *,
    fee_velocity_sol_min: float,
) -> DlmmSignal:
    """Apply one research-grid configuration to one canonical observation."""
    return evaluate_canonical_state(
        state,
        fee_velocity_sol_min,
        min_fee_velocity=config.min_fee_velocity,
        max_drain=config.max_drain,
        min_score=config.min_score,
    )


def rank_results(results: list[StrategyResult]):
    return sorted(
        results,
        key=lambda r: (
            r.metrics["profit_factor"],
            r.metrics["net_pnl"],
            -r.metrics["max_drawdown"],
        ),
        reverse=True,
    )
