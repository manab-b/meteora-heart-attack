from __future__ import annotations

from dataclasses import dataclass
import random


@dataclass(frozen=True)
class MonteCarloResult:
    runs: int
    median_final_pnl: float
    p05_final_pnl: float
    p95_final_pnl: float
    median_max_drawdown: float
    p95_max_drawdown: float
    probability_negative: float


def _max_drawdown(values: list[float]) -> float:
    peak = 0.0
    max_dd = 0.0
    for value in values:
        peak = max(peak, value)
        max_dd = max(max_dd, peak - value)
    return max_dd


def _percentile(values: list[float], q: float) -> float:
    if not values:
        raise ValueError("values must not be empty")
    ordered = sorted(values)
    index = (len(ordered) - 1) * q
    lower = int(index)
    upper = min(lower + 1, len(ordered) - 1)
    fraction = index - lower
    return ordered[lower] + (ordered[upper] - ordered[lower]) * fraction


def bootstrap_trade_pnl(
    trade_pnl: list[float],
    runs: int = 10_000,
    trades_per_run: int | None = None,
    seed: int = 42,
) -> MonteCarloResult:
    if not trade_pnl:
        raise ValueError("trade_pnl must not be empty")
    if runs <= 0:
        raise ValueError("runs must be positive")
    count = len(trade_pnl) if trades_per_run is None else trades_per_run
    if count <= 0:
        raise ValueError("trades_per_run must be positive")

    rng = random.Random(seed)
    finals: list[float] = []
    drawdowns: list[float] = []
    for _ in range(runs):
        equity = 0.0
        path = []
        for _ in range(count):
            equity += rng.choice(trade_pnl)
            path.append(equity)
        finals.append(equity)
        drawdowns.append(_max_drawdown(path))

    return MonteCarloResult(
        runs=runs,
        median_final_pnl=_percentile(finals, 0.50),
        p05_final_pnl=_percentile(finals, 0.05),
        p95_final_pnl=_percentile(finals, 0.95),
        median_max_drawdown=_percentile(drawdowns, 0.50),
        p95_max_drawdown=_percentile(drawdowns, 0.95),
        probability_negative=sum(value < 0 for value in finals) / runs,
    )
