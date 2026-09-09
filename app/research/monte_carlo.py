from __future__ import annotations

import random
from dataclasses import dataclass


@dataclass(frozen=True)
class MonteCarloSummary:
    runs: int
    p05: float
    median: float
    p95: float
    loss_probability: float


@dataclass(frozen=True)
class BootstrapSummary:
    runs: int
    probability_negative: float
    p05: float
    median: float
    p95: float


def simulate(pnls: list[float], runs: int = 10000, seed: int = 42) -> MonteCarloSummary:
    if not pnls:
        raise ValueError("pnls cannot be empty")
    if runs < 100:
        raise ValueError("runs must be >= 100")
    rng = random.Random(seed)
    finals = [sum(rng.choice(pnls) for _ in pnls) for _ in range(runs)]
    finals.sort()

    def q(p: float) -> float:
        return finals[min(len(finals) - 1, max(0, int((len(finals) - 1) * p)))]

    return MonteCarloSummary(runs, q(.05), q(.50), q(.95), sum(x < 0 for x in finals) / runs)


def bootstrap_trade_pnl(
    pnls: list[float],
    *,
    runs: int = 10000,
    trades_per_run: int | None = None,
    seed: int = 42,
) -> BootstrapSummary:
    if not pnls:
        raise ValueError("pnls cannot be empty")
    if runs < 1:
        raise ValueError("runs must be positive")
    trades = len(pnls) if trades_per_run is None else trades_per_run
    if trades < 1:
        raise ValueError("trades_per_run must be positive")
    rng = random.Random(seed)
    finals = [sum(rng.choice(pnls) for _ in range(trades)) for _ in range(runs)]
    finals.sort()

    def q(p: float) -> float:
        return finals[min(len(finals) - 1, max(0, int((len(finals) - 1) * p)))]

    return BootstrapSummary(
        runs=runs,
        probability_negative=sum(value < 0 for value in finals) / runs,
        p05=q(.05),
        median=q(.50),
        p95=q(.95),
    )
