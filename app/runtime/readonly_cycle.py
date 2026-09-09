from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from app.collector.bin_ingest import ingest_bin_observation
from app.collector.position_ingest import ingest_position_observation
from app.runtime.dedup_store import DedupStore
from app.runtime.idempotency import observation_key


def _ts(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()

@dataclass(frozen=True)
class ReadonlyCycleResult:
    bin_observations: int
    position_observations: int
    duplicate_records: int
    errors: int

class ReadonlyCycle:
    """Persist SDK observations; never signs or submits transactions."""
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.dedup = DedupStore(connection)

    def ingest(self, bin_lines=(), position_lines=()) -> ReadonlyCycleResult:
        duplicate = errors = bins = positions = 0
        for line in bin_lines:
            try:
                payload = json.loads(line)
                if "error" in payload: continue
                observed = str(payload["observed_at"]); ts = _ts(observed)
                key = observation_key(
                    f"bin:{payload['pool_address']}:{payload['bin_id']}", ts
                )
                if not self.dedup.claim(key, ts): duplicate += 1; continue
                ingest_bin_observation(self.connection, payload); bins += 1
            except Exception:
                errors += 1
        for line in position_lines:
            try:
                payload = json.loads(line)
                if "error" in payload: continue
                observed = str(payload["observed_at"]); ts = _ts(observed)
                key = observation_key(
                    f"position:{payload['pool_address']}:{payload['position_address']}", ts
                )
                if not self.dedup.claim(key, ts): duplicate += 1; continue
                ingest_position_observation(self.connection, payload); positions += 1
            except Exception:
                errors += 1
        self.connection.commit()
        return ReadonlyCycleResult(bins, positions, duplicate, errors)
