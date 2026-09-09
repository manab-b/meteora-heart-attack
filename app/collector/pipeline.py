from __future__ import annotations

import sqlite3
from datetime import datetime

from app.collector.schema import CollectorBatch
from app.positions.model import PositionSnapshot
from app.positions.store import insert_position
from app.storage.observations import insert_observation


class CollectorPipeline:
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection

    def persist_position(self, snapshot: PositionSnapshot) -> bool:
        try:
            datetime.fromisoformat(snapshot.observed_at.replace("Z", "+00:00"))
        except ValueError:
            return False
        insert_position(self.connection, snapshot)
        return True

    def persist_observation(self, pool_address: str, bins: int, timestamp: float,
                            price: float, volume_usd: float,
                            fee_velocity_sol_min: float, drain_score: float,
                            range_survival_seconds: float, in_range: bool) -> bool:
        insert_observation(
            self.connection, pool_address, bins, timestamp, price, volume_usd,
            fee_velocity_sol_min, drain_score, range_survival_seconds, in_range
        )
        return True
