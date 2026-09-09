from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable


@dataclass(frozen=True)
class BinLiquidityObservation:
    pool_address: str
    bin_id: int
    active_bin_id: int
    price: str
    x_amount_raw: str
    y_amount_raw: str
    observed_at: str


def _first(payload: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        value = payload.get(key)
        if value is not None:
            return value
    return None


def _bin_rows(payload: dict[str, Any]) -> Iterable[dict[str, Any]]:
    rows = _first(payload, "bins", "bin_liquidity", "binLiquidity")
    if rows is None and isinstance(payload.get("data"), dict):
        rows = _first(payload["data"], "bins", "bin_liquidity", "binLiquidity")
    if not isinstance(rows, list):
        return ()
    return (row for row in rows if isinstance(row, dict))


def normalize_bin_liquidity(
    *,
    pool_address: str,
    payload: dict[str, Any],
    observed_at: str,
) -> list[BinLiquidityObservation]:
    """Normalize authoritative bin payloads without converting raw token amounts."""
    root = payload.get("data") if isinstance(payload.get("data"), dict) else payload
    active = _first(root, "active_bin_id", "activeBinId", "activeBin")
    if active is None:
        raise ValueError("bin payload is missing active bin id")
    active_bin_id = int(active)
    result: list[BinLiquidityObservation] = []
    for row in _bin_rows(root):
        bin_id = _first(row, "bin_id", "binId")
        x_amount = _first(row, "x_amount", "xAmount", "x_amount_raw")
        y_amount = _first(row, "y_amount", "yAmount", "y_amount_raw")
        price = _first(row, "price", "price_per_token", "pricePerToken")
        if bin_id is None or x_amount is None or y_amount is None or price is None:
            continue
        result.append(
            BinLiquidityObservation(
                pool_address=pool_address,
                bin_id=int(bin_id),
                active_bin_id=active_bin_id,
                price=str(price),
                x_amount_raw=str(x_amount),
                y_amount_raw=str(y_amount),
                observed_at=observed_at,
            )
        )
    return result
