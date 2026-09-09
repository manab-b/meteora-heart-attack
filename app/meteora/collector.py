from __future__ import annotations
import time, sqlite3
from app.meteora.dlmm_client import DlmmDataClient
from app.meteora.normalizer import normalize_pools
from app.storage.raw_observations import insert_observation
from app.storage.watchlist import replace_watchlist
from app.discovery.scoring import opportunity_score

def collect_once(conn:sqlite3.Connection, client:DlmmDataClient|None=None, max_pools:int=25):
    client=client or DlmmDataClient()
    pools=normalize_pools(client.pools())
    pools=sorted(pools,key=lambda p:opportunity_score(volume_24h_usd=p.volume_24h_usd,tvl_usd=p.tvl_usd,fee_24h_usd=p.fee_24h_usd),reverse=True)
    selected=pools[:max_pools]
    scores={p.address:opportunity_score(volume_24h_usd=p.volume_24h_usd,tvl_usd=p.tvl_usd,fee_24h_usd=p.fee_24h_usd) for p in selected}
    replace_watchlist(conn,selected,scores)
    for p in selected:
        try: insert_observation(conn,p.address,client.ohlcv(p.address))
        except Exception: continue
    return selected
