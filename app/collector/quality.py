from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class QualityResult:
    valid: bool
    reasons: tuple[str, ...]

def validate_snapshot(price: float, observed_at: str, max_age_seconds: float = 120) -> QualityResult:
    reasons: list[str] = []
    if price <= 0:
        reasons.append("NON_POSITIVE_PRICE")
    try:
        dt = datetime.fromisoformat(observed_at.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        age = (datetime.now(timezone.utc) - dt).total_seconds()
        if age > max_age_seconds:
            reasons.append("STALE")
        if age < -30:
            reasons.append("FUTURE_TIMESTAMP")
    except ValueError:
        reasons.append("INVALID_TIMESTAMP")
    return QualityResult(not reasons, tuple(reasons))
