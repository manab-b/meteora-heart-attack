from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class ObservationHealth:
    fresh: bool
    age_seconds: float
    interval_seconds: float | None
    reason: str

def assess(now: datetime, observed_at: datetime, interval_seconds: float,
           max_age_multiplier: float = 2.5) -> ObservationHealth:
    if observed_at.tzinfo is None: observed_at = observed_at.replace(tzinfo=timezone.utc)
    if now.tzinfo is None: now = now.replace(tzinfo=timezone.utc)
    age=max(0.0,(now-observed_at).total_seconds())
    if interval_seconds <= 0: return ObservationHealth(False,age,None,"invalid_interval")
    fresh=age <= interval_seconds*max_age_multiplier
    return ObservationHealth(fresh,age,interval_seconds,"fresh" if fresh else "stale")
