from __future__ import annotations
from dataclasses import dataclass
from app.metrics.score import opportunity_score

@dataclass(frozen=True)
class Candidate:
    pool_address: str
    volume_usd: float
    fee_sol_per_minute: float
    range_survival_seconds: float
    drain_score: float

def rank(candidates: list[Candidate], limit: int = 20) -> list[Candidate]:
    return sorted(
        candidates,
        key=lambda c: opportunity_score(
            c.fee_sol_per_minute, c.range_survival_seconds, c.drain_score
        ),
        reverse=True,
    )[:limit]
