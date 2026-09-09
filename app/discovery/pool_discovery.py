from __future__ import annotations
from dataclasses import dataclass
from typing import Any, Iterable

@dataclass(frozen=True)
class PoolCandidate:
    address: str
    tvl_usd: float
    volume_24h_usd: float
    fee_24h_usd: float
    raw: dict[str, Any]

def _num(v: Any) -> float:
    try: return float(v or 0)
    except (TypeError, ValueError): return 0.0

def discover(payload: Any, min_tvl_usd: float=1_000, min_volume_24h_usd: float=0) -> list[PoolCandidate]:
    items = payload.get("data", payload) if isinstance(payload, dict) else payload
    if not isinstance(items, list): raise ValueError("unexpected pools response shape")
    out=[]
    for p in items:
        if not isinstance(p, dict): continue
        address=str(p.get("address") or p.get("pool_address") or "")
        if not address: continue
        tvl=_num(p.get("tvl") or p.get("tvl_usd"))
        vol=_num(p.get("volume_24h") or p.get("volume_24h_usd"))
        fee=_num(p.get("fees_24h") or p.get("fee_24h_usd"))
        if tvl >= min_tvl_usd and vol >= min_volume_24h_usd:
            out.append(PoolCandidate(address,tvl,vol,fee,p))
    return out
