from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class PoolObservation:
    address: str
    observed_at: float
    raw: dict[str,Any]

def normalize_pool(payload: Any, observed_at: float) -> PoolObservation:
    if not isinstance(payload, dict):
        raise ValueError("pool payload must be an object")
    address=str(payload.get("address") or payload.get("pool_address") or "")
    if not address:
        raise ValueError("pool address missing")
    return PoolObservation(address,observed_at,payload)
