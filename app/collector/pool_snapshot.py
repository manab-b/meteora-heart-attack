from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Optional


@dataclass(frozen=True)
class PoolSnapshot:
    address: str
    observed_at: float
    current_price: Optional[float]
    tvl_usd: Optional[float]
    volume_5m_usd: Optional[float]
    volume_30m_usd: Optional[float]
    volume_1h_usd: Optional[float]
    volume_24h_usd: Optional[float]
    fee_5m_usd: Optional[float]
    fee_30m_usd: Optional[float]
    fee_1h_usd: Optional[float]
    fee_24h_usd: Optional[float]
    dynamic_fee_pct: Optional[float]
    bin_step: Optional[int]
    token_x_symbol: Optional[str]
    token_y_symbol: Optional[str]
    token_x_price_usd: Optional[float]
    token_y_price_usd: Optional[float]
    blacklisted: Optional[bool]


def _number(value: Any) -> Optional[float]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _int(value: Any) -> Optional[int]:
    if value is None or isinstance(value, bool):
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _pick(data: Mapping[str, Any], *keys: str) -> Any:
    for key in keys:
        if key in data and data[key] is not None:
            return data[key]
    return None


def _nested(data: Mapping[str, Any], parent: str, *keys: str) -> Any:
    value = data.get(parent)
    if not isinstance(value, Mapping):
        return None
    return _pick(value, *keys)


def normalize_pool_snapshot(
    data: Mapping[str, Any], observed_at: float
) -> PoolSnapshot:
    """Normalize a Meteora pool API payload without inventing missing values."""
    address = _pick(data, "address", "pool_address")
    if not address:
        raise ValueError("pool payload must contain address")

    config = data.get("pool_config")
    config = config if isinstance(config, Mapping) else {}

    token_x = data.get("token_x")
    token_x = token_x if isinstance(token_x, Mapping) else {}
    token_y = data.get("token_y")
    token_y = token_y if isinstance(token_y, Mapping) else {}

    return PoolSnapshot(
        address=str(address),
        observed_at=float(observed_at),
        current_price=_number(_pick(data, "current_price", "price")),
        tvl_usd=_number(_pick(data, "tvl", "tvl_usd")),
        volume_5m_usd=_number(_pick(data, "volume_5m", "volume_5m_usd")),
        volume_30m_usd=_number(_pick(data, "volume_30m", "volume_30m_usd")),
        volume_1h_usd=_number(_pick(data, "volume_1h", "volume_1h_usd")),
        volume_24h_usd=_number(_pick(data, "volume_24h", "volume_24h_usd")),
        fee_5m_usd=_number(_pick(data, "fees_5m", "fee_5m", "fee_5m_usd")),
        fee_30m_usd=_number(_pick(data, "fees_30m", "fee_30m", "fee_30m_usd")),
        fee_1h_usd=_number(_pick(data, "fees_1h", "fee_1h", "fee_1h_usd")),
        fee_24h_usd=_number(_pick(data, "fees_24h", "fee_24h", "fee_24h_usd")),
        dynamic_fee_pct=_number(_pick(data, "dynamic_fee_pct")),
        bin_step=_int(_pick(data, "bin_step", "bin_step_bps" , "bin_step_basis_points"))
        if _pick(data, "bin_step", "bin_step_bps", "bin_step_basis_points") is not None
        else _int(config.get("bin_step")),
        token_x_symbol=_pick(token_x, "symbol") or _pick(data, "token_x_symbol"),
        token_y_symbol=_pick(token_y, "symbol") or _pick(data, "token_y_symbol"),
        token_x_price_usd=_number(_pick(token_x, "price", "price_usd")),
        token_y_price_usd=_number(_pick(token_y, "price", "price_usd")),
        blacklisted=_pick(data, "blacklisted"),
    )
