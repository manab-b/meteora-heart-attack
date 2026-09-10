from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable


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


@dataclass(frozen=True)
class DlmmPnl:
    entry_value_sol: float
    current_value_sol: float
    hodl_value_sol: float
    fees_sol: float
    il_pct: float
    net_pnl_sol: float
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


def dlmm_pnl_sol(
    entry_x_amount: float,
    entry_y_amount: float,
    current_x_amount: float,
    current_y_amount: float,
    entry_x_sol_price: float,
    entry_y_sol_price: float,
    current_x_sol_price: float,
    current_y_sol_price: float,
    fees_sol: float = 0.0,
) -> DlmmPnl:
    """Calculate DLMM position PnL in SOL without price or fee estimation."""
    amounts = (entry_x_amount, entry_y_amount, current_x_amount, current_y_amount)
    if any(value < 0 for value in amounts):
        raise ValueError("token amounts must be non-negative")
    prices = (
        entry_x_sol_price,
        entry_y_sol_price,
        current_x_sol_price,
        current_y_sol_price,
    )
    if any(value <= 0 for value in prices):
        raise ValueError("token SOL prices must be positive")
    if fees_sol < 0:
        raise ValueError("fees_sol must be non-negative")

    entry_value = entry_x_amount * entry_x_sol_price + entry_y_amount * entry_y_sol_price
    current_value = current_x_amount * current_x_sol_price + current_y_amount * current_y_sol_price
    hodl_value = entry_x_amount * current_x_sol_price + entry_y_amount * current_y_sol_price
    if entry_value <= 0 or hodl_value <= 0:
        raise ValueError("entry and HODL benchmark values must be positive")

    il_pct = (current_value / hodl_value - 1.0) * 100.0
    net_pnl_sol = current_value + fees_sol - entry_value
    net_return_pct = (net_pnl_sol / entry_value) * 100.0
    return DlmmPnl(
        entry_value_sol=entry_value,
        current_value_sol=current_value,
        hodl_value_sol=hodl_value,
        fees_sol=fees_sol,
        il_pct=il_pct,
        net_pnl_sol=net_pnl_sol,
        net_return_pct=net_return_pct,
    )


def max_drawdown(values: Iterable[float]) -> float:
    """Return absolute peak-to-trough drawdown for an equity/value series."""
    iterator = iter(values)
    try:
        peak = float(next(iterator))
    except StopIteration:
        return 0.0
    if peak < 0:
        raise ValueError("equity values must be non-negative")
    drawdown = 0.0
    for value in iterator:
        value = float(value)
        if value < 0:
            raise ValueError("equity values must be non-negative")
        peak = max(peak, value)
        drawdown = max(drawdown, peak - value)
    return drawdown
