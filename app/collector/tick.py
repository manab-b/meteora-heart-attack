from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class Tick:
    pool_address: str
    observed_at: str
    price: float
    active_bin: int | None
    tvl_usd: float | None
    dynamic_fee_pct: float | None
    source: str
    data_age_seconds: float | None = None

def utc_now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()
