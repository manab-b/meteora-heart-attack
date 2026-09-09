from __future__ import annotations

from dataclasses import dataclass

from app.valuation.model import fee_sol_value


@dataclass(frozen=True)
class FeeQuote:
    fee_x_raw: int
    fee_y_raw: int
    x_decimals: int
    y_decimals: int
    x_sol_price: float
    y_sol_price: float
    observed_at: float
    source: str

    def value_sol(self) -> float:
        return fee_sol_value(
            self.fee_x_raw,
            self.fee_y_raw,
            self.x_decimals,
            self.y_decimals,
            self.x_sol_price,
            self.y_sol_price,
        )


def quote_fee_delta(
    *,
    fee_x_raw: int | str,
    fee_y_raw: int | str,
    x_decimals: int,
    y_decimals: int,
    x_sol_price: float | None,
    y_sol_price: float | None,
) -> float | None:
    """Return SOL value only when both token/SOL prices are real and valid."""
    if x_sol_price is None or y_sol_price is None:
        return None
    return fee_sol_value(
        fee_x_raw,
        fee_y_raw,
        x_decimals,
        y_decimals,
        x_sol_price,
        y_sol_price,
    )
