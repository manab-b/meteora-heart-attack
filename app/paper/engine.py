from __future__ import annotations

from dataclasses import dataclass
from time import time

from app.metrics.position_pnl import dlmm_pnl_from_canonical_states, position_value_usd
from app.paper.canonical_position import CanonicalPositionState


@dataclass
class PaperPosition:
    id: str
    pool_address: str
    entry_time: float
    entry_price: float
    min_price: float
    max_price: float
    deposit_sol: float
    fee_sol: float = 0.0
    claimed_sol: float = 0.0
    status: str = "OPEN"
    out_of_range_since: float | None = None
    entry_x_amount: float | None = None
    entry_y_amount: float | None = None
    current_x_amount: float | None = None
    current_y_amount: float | None = None
    entry_x_price_usd: float | None = None
    entry_y_price_usd: float | None = None
    current_x_price_usd: float | None = None
    current_y_price_usd: float | None = None


class PaperEngine:
    def __init__(self, claim_threshold_sol: float = 0.02, out_of_range_seconds: int = 20):
        self.positions: dict[str, PaperPosition] = {}
        self.events: list[dict] = []
        self.claim_threshold_sol = claim_threshold_sol
        self.out_of_range_seconds = out_of_range_seconds

    def open(
        self,
        position_id: str,
        pool_address: str,
        price: float,
        min_price: float,
        max_price: float,
        deposit_sol: float,
        timestamp: float | None = None,
        *,
        x_amount: float | None = None,
        y_amount: float | None = None,
        x_price_usd: float | None = None,
        y_price_usd: float | None = None,
    ) -> PaperPosition:
        if position_id in self.positions:
            raise ValueError("position already exists")
        if deposit_sol <= 0:
            raise ValueError("deposit_sol must be positive")
        if min_price > max_price:
            raise ValueError("min_price must not exceed max_price")
        now = time() if timestamp is None else timestamp
        p = PaperPosition(
            position_id,
            pool_address,
            now,
            price,
            min_price,
            max_price,
            deposit_sol,
            entry_x_amount=x_amount,
            entry_y_amount=y_amount,
            current_x_amount=x_amount,
            current_y_amount=y_amount,
            entry_x_price_usd=x_price_usd,
            entry_y_price_usd=y_price_usd,
            current_x_price_usd=x_price_usd,
            current_y_price_usd=y_price_usd,
        )
        self.positions[position_id] = p
        self._event("OPEN", p, price, now)
        return p

    def tick(
        self,
        position_id: str,
        price: float,
        fee_delta_sol: float,
        timestamp: float | None = None,
        *,
        x_amount: float | None = None,
        y_amount: float | None = None,
        x_price_usd: float | None = None,
        y_price_usd: float | None = None,
    ) -> None:
        p = self.positions[position_id]
        if p.status != "OPEN":
            return
        now = time() if timestamp is None else timestamp
        if fee_delta_sol < 0:
            raise ValueError("fee_delta_sol must be non-negative")
        p.fee_sol += fee_delta_sol
        if x_amount is not None:
            p.current_x_amount = x_amount
        if y_amount is not None:
            p.current_y_amount = y_amount
        if x_price_usd is not None:
            p.current_x_price_usd = x_price_usd
        if y_price_usd is not None:
            p.current_y_price_usd = y_price_usd
        in_range = p.min_price <= price <= p.max_price
        if p.fee_sol - p.claimed_sol >= self.claim_threshold_sol:
            p.claimed_sol = p.fee_sol
            self._event("CLAIM_TO_SOL", p, price, now)
        if in_range:
            p.out_of_range_since = None
        elif p.out_of_range_since is None:
            p.out_of_range_since = now
        elif now - p.out_of_range_since >= self.out_of_range_seconds:
            self.close(position_id, price, "OUT_OF_RANGE", now)

    def close(self, position_id: str, price: float, reason: str, timestamp: float | None = None) -> None:
        p = self.positions[position_id]
        if p.status != "OPEN":
            return
        now = time() if timestamp is None else timestamp
        p.claimed_sol = p.fee_sol
        p.status = "CLOSED"
        self._event(reason, p, price, now)

    def mark_to_market_usd(self, position_id: str) -> float | None:
        p = self.positions[position_id]
        if None in (
            p.current_x_amount,
            p.current_y_amount,
            p.current_x_price_usd,
            p.current_y_price_usd,
        ):
            return None
        return position_value_usd(
            p.current_x_amount,
            p.current_y_amount,
            p.current_x_price_usd,
            p.current_y_price_usd,
        ).value_usd

    def mark_to_market_sol_from_canonical(self, state: CanonicalPositionState) -> float | None:
        """Use the authoritative canonical position mark without estimating missing data."""
        if not state.eligible_for_mtm:
            return None
        return state.position_value_sol

    def dlmm_pnl_from_canonical(
        self,
        entry_state: CanonicalPositionState,
        current_state: CanonicalPositionState,
        fees_sol: float,
    ):
        """Calculate paper DLMM PnL from authoritative canonical observations."""
        return dlmm_pnl_from_canonical_states(entry_state, current_state, fees_sol=fees_sol)

    def _event(self, action: str, p: PaperPosition, price: float, timestamp: float) -> None:
        self.events.append(
            {
                "timestamp": timestamp,
                "action": action,
                "position_id": p.id,
                "pool_address": p.pool_address,
                "price": price,
                "fee_sol": p.fee_sol,
                "claimed_sol": p.claimed_sol,
                "status": p.status,
            }
        )
