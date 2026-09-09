from __future__ import annotations
import sqlite3
from dataclasses import dataclass
from statistics import median

@dataclass(frozen=True)
class TradeSummary:
    trades: int
    closed: int
    total_fees_sol: float
    median_fees_sol: float
    total_duration_seconds: float
    median_duration_seconds: float
    win_rate: float
    total_fee_return_sol: float

def summarize_trades(connection: sqlite3.Connection) -> TradeSummary:
    rows = connection.execute("""
        SELECT entry_time, fee_sol, status
        FROM paper_positions
        ORDER BY entry_time
    """).fetchall()
    fees=[float(r[1]) for r in rows]
    closed=sum(r[2]=="CLOSED" for r in rows)
    durations=[]
    for pid, in connection.execute("SELECT position_id FROM paper_positions WHERE status='CLOSED'"):
        x=connection.execute("SELECT MIN(timestamp), MAX(timestamp) FROM paper_position_events WHERE position_id=?", (pid,)).fetchone()
        if x[0] is not None and x[1] is not None: durations.append(max(0.0,float(x[1])-float(x[0])))
    wins=sum(f>0 for f in fees if f is not None)
    return TradeSummary(
        trades=len(rows), closed=closed,
        total_fees_sol=sum(fees),
        median_fees_sol=median(fees) if fees else 0.0,
        total_duration_seconds=sum(durations),
        median_duration_seconds=median(durations) if durations else 0.0,
        win_rate=(wins/closed) if closed else 0.0,
        total_fee_return_sol=sum(fees),
    )
