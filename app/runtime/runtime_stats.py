from __future__ import annotations
import sqlite3
from dataclasses import dataclass

@dataclass(frozen=True)
class RunnerStats:
    pools: int
    open_positions: int
    closed_positions: int
    total_fees_sol: float
    total_pnl_usd: float

def snapshot(connection: sqlite3.Connection) -> RunnerStats:
    def scalar(sql: str):
        return connection.execute(sql).fetchone()[0]
    tables={r[0] for r in connection.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    if "paper_positions" not in tables:
        return RunnerStats(0,0,0,0.0,0.0)
    pools=scalar("SELECT COUNT(DISTINCT token) FROM paper_positions")
    open_positions=scalar("SELECT COUNT(*) FROM paper_positions WHERE status='OPEN'")
    closed=scalar("SELECT COUNT(*) FROM paper_positions WHERE status='CLOSED'")
    fees=float(scalar("SELECT COALESCE(SUM(fees_sol),0) FROM paper_positions"))
    return RunnerStats(pools,open_positions,closed,fees,0.0)
