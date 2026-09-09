from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from .http import MeteoraHttpClient
from .rate_limit import RateLimiter


@dataclass(frozen=True)
class PoolSnapshot:
    address: str
    current_price: float | None
    tvl_usd: float | None
    volume_24h_usd: float | None
    fees_24h_usd: float | None
    bin_step: int | None
    base_fee_pct: float | None
    dynamic_fee_pct: float | None
    max_fee_pct: float | None
    protocol_fee_pct: float | None
    raw: dict[str, Any]


def _number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _first_number(*values: Any) -> float | None:
    for value in values:
        parsed = _number(value)
        if parsed is not None:
            return parsed
    return None


def normalize_pool(data: dict[str, Any]) -> PoolSnapshot:
    config = data.get("pool_config") or data.get("poolConfig") or {}
    volume = data.get("volume") or {}
    fees = data.get("fees") or {}
    return PoolSnapshot(
        address=str(data.get("address") or data.get("publicKey") or ""),
        current_price=_first_number(data.get("current_price"), data.get("currentPrice")),
        tvl_usd=_first_number(data.get("tvl"), data.get("tvl_usd"), data.get("tvlUsd"), config.get("tvl")),
        volume_24h_usd=_first_number(volume.get("24h"), volume.get("24H"), data.get("volume_24h"), data.get("volume_24h_usd")),
        fees_24h_usd=_first_number(fees.get("24h"), fees.get("24H"), data.get("fees_24h"), data.get("fees_24h_usd")),
        bin_step=int(config["bin_step"]) if config.get("bin_step") is not None else None,
        base_fee_pct=_first_number(config.get("base_fee_pct"), config.get("baseFeePct")),
        dynamic_fee_pct=_first_number(data.get("dynamic_fee_pct"), data.get("dynamicFeePct")),
        max_fee_pct=_first_number(config.get("max_fee_pct"), config.get("maxFeePct")),
        protocol_fee_pct=_first_number(config.get("protocol_fee_pct"), config.get("protocolFeePct")),
        raw=data,
    )


class PoolReader:
    def __init__(self, client: MeteoraHttpClient, requests_per_second: float = 20.0):
        self.client = client
        self.limiter = RateLimiter(requests_per_second)

    def get_pool(self, address: str) -> PoolSnapshot:
        self.limiter.wait()
        return normalize_pool(self.client.get_json(f"/pools/{address}"))

    def get_ohlcv(self, address: str, timeframe: str = "5m") -> dict[str, Any]:
        self.limiter.wait()
        return self.client.get_json(f"/pools/{address}/ohlcv", {"timeframe": timeframe})

    def get_volume_history(self, address: str, timeframe: str = "5m") -> dict[str, Any]:
        self.limiter.wait()
        return self.client.get_json(f"/pools/{address}/volume/history", {"timeframe": timeframe})
