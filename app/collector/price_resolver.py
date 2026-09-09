from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol


@dataclass(frozen=True)
class TokenPrice:
    mint: str
    price_usd: float
    observed_at: float
    source: str

    def __post_init__(self) -> None:
        if not self.mint:
            raise ValueError("mint must be non-empty")
        if self.price_usd <= 0:
            raise ValueError("price_usd must be positive")


class PriceResolver(Protocol):
    def resolve(self, mint: str, observed_at: float) -> TokenPrice | None:
        ...


def resolve_pair(
    resolver: PriceResolver,
    x_mint: str,
    y_mint: str,
    observed_at: float,
) -> tuple[TokenPrice, TokenPrice] | None:
    """Resolve both token prices or return None; never fabricate a quote."""
    x = resolver.resolve(x_mint, observed_at)
    y = resolver.resolve(y_mint, observed_at)
    if x is None or y is None:
        return None
    return x, y
