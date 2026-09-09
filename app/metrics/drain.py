from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class DrainObservation:
    previous_tvl_usd: float
    current_tvl_usd: float
    elapsed_seconds: float

    @property
    def absolute_change_usd(self) -> float:
        return self.current_tvl_usd - self.previous_tvl_usd

    @property
    def drain_rate_per_minute(self) -> float:
        """Positive value means observed TVL is declining.

        This is a pool-level signal, not proof of LP withdrawal. Position/bin
        data must be used before classifying the event as actual liquidity drain.
        """
        if self.elapsed_seconds <= 0 or self.previous_tvl_usd <= 0:
            return 0.0
        decline = max(0.0, self.previous_tvl_usd - self.current_tvl_usd)
        return decline / self.previous_tvl_usd / (self.elapsed_seconds / 60.0)

    @property
    def drain_score(self) -> float:
        if self.previous_tvl_usd <= 0:
            return 0.0
        return max(0.0, min(1.0, (self.previous_tvl_usd - self.current_tvl_usd) / self.previous_tvl_usd))


def liquidity_drain_score(previous_total: float, current_total: float) -> float:
    if previous_total < 0 or current_total < 0:
        raise ValueError("liquidity values must be non-negative")
    if previous_total == 0:
        return 0.0
    drop = (previous_total - current_total) / previous_total
    return max(0.0, min(1.0, drop))


def liquidity_drain_rate(previous_liquidity_usd: float, current_liquidity_usd: float, elapsed_seconds: float) -> float:
    if previous_liquidity_usd < 0 or current_liquidity_usd < 0:
        raise ValueError("liquidity values must be non-negative")
    if elapsed_seconds <= 0:
        raise ValueError("elapsed_seconds must be positive")
    if previous_liquidity_usd == 0:
        return 0.0
    depletion = max(0.0, previous_liquidity_usd - current_liquidity_usd) / previous_liquidity_usd
    return depletion * 60.0 / elapsed_seconds
