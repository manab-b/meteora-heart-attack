from __future__ import annotations
from dataclasses import dataclass
from typing import Any

@dataclass(frozen=True)
class Tick:
    observed_at: float
    price: float
    volume_usd: float = 0.0
    fee_usd: float = 0.0
    liquidity_usd: float = 0.0
    in_range: bool = True
    rug_flags: tuple[str,...] = ()

def _num(v:Any,default=0.0)->float:
    try: return float(v)
    except (TypeError,ValueError): return default

def normalize_tick(raw:dict[str,Any], observed_at:float|None=None)->Tick:
    ts=_num(raw.get("timestamp",raw.get("time",observed_at or 0)))
    price=_num(raw.get("price",raw.get("close",raw.get("close_price",0))))
    volume=_num(raw.get("volume_usd",raw.get("volume",0)))
    fee=_num(raw.get("fee_usd",raw.get("fees_usd",0)))
    liquidity=_num(raw.get("liquidity_usd",raw.get("tvl",0)))
    return Tick(ts,price,volume,fee,liquidity,bool(raw.get("in_range",True)),tuple(raw.get("rug_flags",()) or ()))
