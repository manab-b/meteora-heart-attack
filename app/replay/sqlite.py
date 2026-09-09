from __future__ import annotations
import sqlite3
from app.strategy.backtest import Observation

def load_observations(connection: sqlite3.Connection, pool_address: str) -> list[Observation]:
    rows = connection.execute(
        """SELECT timestamp, price, volume_usd, fee_velocity_sol_min,
                  drain_score, range_survival_seconds, in_range
           FROM observations
           WHERE pool_address = ?
           ORDER BY timestamp ASC""",
        (pool_address,),
    ).fetchall()
    return [Observation(float(a), float(b), float(c), float(d), float(e), float(f), bool(g))
            for a,b,c,d,e,f,g in rows]
