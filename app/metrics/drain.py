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
        """Positive value means TVL is leaving the pool.

        This is a TVL-change signal, not proof that LPs withdrew liquidity.
        Position/account data is required before labeling it a true drain event.
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
    if previous_total <= 0:
        return 0.0
    drop = (previous_total - current_total) / previous_total
    return max(0.0, min(1.0, drop))
