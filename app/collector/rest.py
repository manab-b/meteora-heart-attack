from __future__ import annotations
from typing import Any
from app.collector.tick import Tick, utc_now_iso
from app.meteora.client import MeteoraClient

def pool_to_tick(pool: dict[str, Any], pool_address: str) -> Tick:
    return Tick(
        pool_address=pool_address,
        observed_at=utc_now_iso(),
        price=float(pool.get("current_price") or 0),
        active_bin=int(pool["active_bin"]) if pool.get("active_bin") is not None else None,
        tvl_usd=float(pool.get("tvl") or 0),
        dynamic_fee_pct=float(pool.get("dynamic_fee_pct") or 0),
        source="meteora-rest",
    )

def fetch_pool_tick(client: MeteoraClient, pool_address: str) -> Tick:
    # Single-pool endpoint is intentionally isolated so the collector can later
    # swap this source for RPC/SDK data without changing storage.
    import httpx
    response = httpx.get(
        f"{client.base_url}/pools/{pool_address}",
        timeout=client.timeout,
    )
    response.raise_for_status()
    payload = response.json()
    data = payload.get("data", payload)
    return pool_to_tick(data, pool_address)
