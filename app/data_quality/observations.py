from __future__ import annotations

import math
import sqlite3
from dataclasses import dataclass


@dataclass(frozen=True)
class ObservationQualityConfig:
    # A single observation is sufficient to start paper simulation; research
    # qualification still happens later through the robust data/research gates.
    min_observations: int = 1
    max_gap_seconds: float = 300.0
    require_in_range: bool = True


@dataclass(frozen=True)
class ObservationQuality:
    ok: bool
    reasons: tuple[str, ...]
    count: int
    latest_timestamp: float | None
    max_gap_seconds: float | None


def assess_observation_quality(
    connection: sqlite3.Connection,
    pool_address: str,
    *,
    config: ObservationQualityConfig = ObservationQualityConfig(),
) -> ObservationQuality:
    rows = connection.execute(
        """SELECT timestamp, price, volume_usd, fee_velocity_sol_min,
                  drain_score, range_survival_seconds, in_range, bins
           FROM observations
           WHERE pool_address = ?
           ORDER BY timestamp DESC, id DESC
           LIMIT ?""",
        (pool_address, max(config.min_observations, 2)),
    ).fetchall()

    reasons: list[str] = []
    count = len(rows)
    latest_timestamp = float(rows[0][0]) if rows else None
    if count < config.min_observations:
        reasons.append("INSUFFICIENT_OBSERVATIONS")

    max_gap: float | None = None
    if len(rows) >= 2:
        timestamps = [float(row[0]) for row in rows]
        gaps = [max(0.0, timestamps[i] - timestamps[i + 1]) for i in range(len(timestamps) - 1)]
        max_gap = max(gaps) if gaps else 0.0
        if max_gap > config.max_gap_seconds:
            reasons.append("TIMESTAMP_GAP")

    for row in rows:
        timestamp, price, volume_usd, fee_velocity, drain_score, survival, in_range, bins = row
        values = (timestamp, price, volume_usd, fee_velocity, drain_score, survival, bins)
        if not all(math.isfinite(float(value)) for value in values):
            reasons.append("NON_FINITE_OBSERVATION")
            break
        if float(price) <= 0 or float(volume_usd) < 0 or float(fee_velocity) < 0:
            reasons.append("INVALID_OBSERVATION_VALUES")
            break
        if int(bins) <= 0:
            reasons.append("MISSING_ACTIVE_BINS")
            break

    if config.require_in_range and rows and not bool(rows[0][6]):
        reasons.append("LATEST_OUT_OF_RANGE")

    return ObservationQuality(
        ok=not reasons,
        reasons=tuple(dict.fromkeys(reasons)),
        count=count,
        latest_timestamp=latest_timestamp,
        max_gap_seconds=max_gap,
    )
