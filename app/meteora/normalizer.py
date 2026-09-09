from __future__ import annotations
from dataclasses import dataclass
from typing import Any

def _pick(d:dict[str,Any], *keys:str, default=0.0):
    for k in keys:
        if k in d and d[k] is not None: return d[k]
    return default

@dataclass(frozen=True)
class NormalizedPool:
    address:str
    tvl_usd:float
    volume_24h_usd:float
    fee_24h_usd:float
    raw:dict[str,Any]

def normalize_pool(raw:dict[str,Any])->NormalizedPool:
    address=str(_pick(raw,"address","pool_address","publicKey",default=""))
    if not address: raise ValueError("pool address missing")
    return NormalizedPool(address,float(_pick(raw,"tvl","tvl_usd","liquidity",default=0)),
      float(_pick(raw,"volume_24h","volume24h","volume_24h_usd",default=0)),
      float(_pick(raw,"fee_24h","fees_24h","fee_24h_usd",default=0)),raw)

def normalize_pools(payload:Any)->list[NormalizedPool]:
    rows=payload.get("data",payload) if isinstance(payload,dict) else payload
    if not isinstance(rows,list): raise ValueError("pool payload is not a list")
    return [normalize_pool(x) for x in rows if isinstance(x,dict)]
