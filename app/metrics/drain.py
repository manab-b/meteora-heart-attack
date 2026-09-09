from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DrainObservation:
    previous_tvl_usd: float
    current_tvl_usd: float
    elapsed_seconds: float
    active_bin_moved: bool = False

    @property
    def absolute_change_usd(self) -> float:
        return self.current_tvl_usd - self.previous_tvl_usd

    @property
    def raw_drain_score(self) -> float:
        if self.previous_tvl_usd <= 0:
            return 0.0
        return max(0.0, min(1.0, (self.previous_tvl_usd - self.current_tvl_usd) / self.previous_tvl_usd))

    @property
    def drain_score(self) -> float:
        """Discount pool-level depletion when active-bin migration explains it."""
        score = self.raw_drain_score
        if self.active_bin_moved:
            score *= 0.35
        return max(0.0, min(1.0, score))

    @property
    def drain_rate_per_minute(self) -> float:
        if self.elapsed_seconds <= 0 or self.previous_tvl_usd <= 0:
            return 0.0
        return self.drain_score / (self.elapsed_seconds / 60.0)


def liquidity_drain_score(
    previous_total: float,
    current_total: float,
    *,
    active_bin_moved: bool = False,
) -> float:
    if previous_total < 0 or current_total < 0:
        raise ValueError("liquidity values must be non-negative")
    if previous_total == 0:
        return 0.0
    score = max(0.0, min(1.0, (previous_total - current_total) / previous_total))
    if active_bin_moved:
        score *= 0.35
    return score


def liquidity_drain_rate(
    previous_liquidity_usd: float,
    current_liquidity_usd: float,
    elapsed_seconds: float,
    *,
    active_bin_moved: bool = False,
) -> float:
    if previous_liquidity_usd < 0 or current_liquidity_usd < 0:
        raise ValueError("liquidity values must be non-negative")
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be positive")
    if previous_liquidity_usd == 0:
        return 0.0
    score = max(0.0, (previous_liquidity_usd - current_liquidity_usd) / previous_liquidity_usd)
    if active_bin_moved:
        score *= 0.35
    return score * 60.0 / elapsed_seconds
