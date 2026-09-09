from __future__ import annotations
import json, sqlite3
from app.research.replay import ReplayTick

def load_ticks(conn: sqlite3.Connection, pool_address: str,
               start: float|None=None, end: float|None=None) -> list[ReplayTick]:
    q="SELECT observed_at,payload_json FROM raw_pool_observations WHERE pool_address=?"
    args=[pool_address]
    if start is not None: q+=" AND observed_at>=?"; args.append(start)
    if end is not None: q+=" AND observed_at<=?"; args.append(end)
    q+=" ORDER BY observed_at ASC"
    return [ReplayTick(row[0],pool_address,json.loads(row[1])) for row in conn.execute(q,args)]
