from __future__ import annotations
from typing import Any
from app.meteora.market_state import Tick,normalize_tick

def extract_rows(payload:Any)->list[dict]:
    rows=payload.get("data",payload) if isinstance(payload,dict) else payload
    if isinstance(rows,dict): rows=rows.get("rows",rows.get("items",[]))
    return [x for x in rows if isinstance(x,dict)] if isinstance(rows,list) else []

def normalize_ohlcv(payload:Any,observed_at:float|None=None)->list[Tick]:
    return [normalize_tick(x,observed_at) for x in extract_rows(payload)]
