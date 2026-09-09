from __future__ import annotations
import sqlite3, time
from app.meteora.dlmm_client import DlmmDataClient
from app.discovery.pool_discovery import discover
from app.discovery.watchlist import build_watchlist
from app.discovery.scoring import opportunity_score
from app.storage.raw_observations import insert_observation
from app.storage.watchlist import replace_watchlist

def run_once(conn:sqlite3.Connection, client:DlmmDataClient|None=None, max_pools:int=25):
    client=client or DlmmDataClient()
    payload=client.pools()
    candidates=discover(payload,min_tvl_usd=1000)
    candidates=sorted(candidates,key=lambda p:opportunity_score(volume_24h_usd=p.volume_24h_usd,tvl_usd=p.tvl_usd,fee_24h_usd=p.fee_24h_usd),reverse=True)
    selected=candidates[:max_pools]
    scores={p.address:opportunity_score(volume_24h_usd=p.volume_24h_usd,tvl_usd=p.tvl_usd,fee_24h_usd=p.fee_24h_usd) for p in selected}
    replace_watchlist(conn,selected,scores)
    for p in selected:
        try:
            insert_observation(conn,p.address,client.ohlcv(p.address),time.time())
        except Exception:
            continue
    return selected
