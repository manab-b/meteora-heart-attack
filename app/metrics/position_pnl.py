from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PositionValue:
    x_amount: float
    y_amount: float
    value_usd: float


@dataclass(frozen=True)
class PositionPnl:
    current_value_usd: float
    hodl_value_usd: float
    fees_usd: float
    il_pct: float
    net_return_pct: float


def position_value_usd(
    x_amount: float,
    y_amount: float,
    x_price_usd: float,
    y_price_usd: float,
) -> PositionValue:
    if x_amount < 0 or y_amount < 0:
        raise ValueError("token amounts must be non-negative")
    if x_price_usd <= 0 or y_price_usd <= 0:
        raise ValueError("token prices must be positive")
    value = x_amount * x_price_usd + y_amount * y_price_usd
    return PositionValue(x_amount, y_amount, value)


def position_pnl(
    entry_x_amount: float,
    entry_y_amount: float,
    current_x_amount: float,
    current_y_amount: float,
    entry_x_price_usd: float,
    entry_y_price_usd: float,
    current_x_price_usd: float,
    current_y_price_usd: float,
    fees_usd: float = 0.0,
) -> PositionPnl:
    if fees_usd < 0:
        raise ValueError("fees_usd must be non-negative")
    entry_value = position_value_usd(
        entry_x_amount, entry_y_amount, entry_x_price_usd, entry_y_price_usd
    ).value_usd
    current_value = position_value_usd(
        current_x_amount, current_y_amount, current_x_price_usd, current_y_price_usd
    ).value_usd
    hodl_value = (
        entry_x_amount * current_x_price_usd
        + entry_y_amount * current_y_price_usd
    )
    if hodl_value <= 0:
        raise ValueError("HODL benchmark value must be positive")
    il_pct = (current_value / hodl_value - 1.0) * 100.0
    net_return_pct = ((current_value + fees_usd) / entry_value - 1.0) * 100.0
    return PositionPnl(
        current_value_usd=current_value,
        hodl_value_usd=hodl_value,
        fees_usd=fees_usd,
        il_pct=il_pct,
        net_return_pct=net_return_pct,
    )
