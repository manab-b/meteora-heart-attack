from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class TokenPrice:
    symbol: str
    usd: float
    sol: float | None = None

    def __post_init__(self) -> None:
        if self.usd <= 0:
            raise ValueError("USD price must be positive")
        if self.sol is not None and self.sol <= 0:
            raise ValueError("SOL price must be positive when supplied")


def raw_to_units(raw_amount: int | str, decimals: int) -> float:
    if decimals < 0:
        raise ValueError("decimals must be non-negative")
    raw = int(raw_amount)
    if raw < 0:
        raise ValueError("raw amount must be non-negative")
    return raw / (10**decimals)


def token_usd_value(raw_amount: int | str, decimals: int, price_usd: float) -> float:
    if price_usd <= 0:
        raise ValueError("price_usd must be positive")
    return raw_to_units(raw_amount, decimals) * price_usd


def fee_sol_value(
    fee_x_raw: int | str,
    fee_y_raw: int | str,
    x_decimals: int,
    y_decimals: int,
    x_sol_price: float | None,
    y_sol_price: float | None,
) -> float:
    """Convert position-level accrued fees to SOL.

    Missing token/SOL prices deliberately return no estimate instead of
    inventing a conversion rate.
    """
    if x_sol_price is None or y_sol_price is None:
        raise ValueError("token SOL prices are required for SOL fee valuation")
    if x_sol_price <= 0 or y_sol_price <= 0:
        raise ValueError("token SOL prices must be positive")
    x = raw_to_units(fee_x_raw, x_decimals) * x_sol_price
    y = raw_to_units(fee_y_raw, y_decimals) * y_sol_price
    return x + y
