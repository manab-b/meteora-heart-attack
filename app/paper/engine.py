from __future__ import annotations
from dataclasses import dataclass
from time import time

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

class PaperEngine:
    def __init__(self, claim_threshold_sol: float = 0.02, out_of_range_seconds: int = 20):
        self.positions: dict[str, PaperPosition] = {}
        self.events: list[dict] = []
        self.claim_threshold_sol = claim_threshold_sol
        self.out_of_range_seconds = out_of_range_seconds

    def open(self, position_id: str, pool_address: str, price: float,
             min_price: float, max_price: float, deposit_sol: float) -> PaperPosition:
        if position_id in self.positions:
            raise ValueError("position already exists")
        p = PaperPosition(position_id, pool_address, time(), price, min_price,
                          max_price, deposit_sol)
        self.positions[position_id] = p
        self._event("OPEN", p, price)
        return p

    def tick(self, position_id: str, price: float, fee_delta_sol: float,
             timestamp: float | None = None) -> None:
        p = self.positions[position_id]
        if p.status != "OPEN":
            return
        now = time() if timestamp is None else timestamp
        p.fee_sol += max(0.0, fee_delta_sol)
        in_range = p.min_price <= price <= p.max_price
        if p.fee_sol - p.claimed_sol >= self.claim_threshold_sol:
            p.claimed_sol = p.fee_sol
            self._event("CLAIM_TO_SOL", p, price)
        if in_range:
            p.out_of_range_since = None
        elif p.out_of_range_since is None:
            p.out_of_range_since = now
        elif now - p.out_of_range_since >= self.out_of_range_seconds:
            self.close(position_id, price, "OUT_OF_RANGE")

    def close(self, position_id: str, price: float, reason: str) -> None:
        p = self.positions[position_id]
        if p.status != "OPEN":
            return
        p.claimed_sol = p.fee_sol
        p.status = "CLOSED"
        self._event(reason, p, price)

    def _event(self, action: str, p: PaperPosition, price: float) -> None:
        self.events.append({
            "timestamp": time(), "action": action, "position_id": p.id,
            "pool_address": p.pool_address, "price": price,
            "fee_sol": p.fee_sol, "claimed_sol": p.claimed_sol,
            "status": p.status,
        })
