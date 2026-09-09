from __future__ import annotations
from dataclasses import dataclass

@dataclass(frozen=True)
class PoolScore:
    pool: str
    score: float
    trades: int
    pnl: float

def rank_pools(results: list[PoolScore]) -> list[PoolScore]:
    return sorted(results,key=lambda x:(x.score,x.pnl,x.trades),reverse=True)
