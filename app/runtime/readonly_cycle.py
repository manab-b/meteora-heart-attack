from __future__ import annotations
import json
import sqlite3
from dataclasses import dataclass
from app.collector.bin_ingest import ingest_jsonl as ingest_bins
from app.collector.position_ingest import ingest_jsonl as ingest_positions
from app.runtime.dedup_store import DedupStore
from app.runtime.idempotency import observation_key

@dataclass(frozen=True)
class ReadonlyCycleResult:
    bin_observations: int
    position_observations: int
    duplicate_records: int
    errors: int

class ReadonlyCycle:
    """Consume SDK JSONL observations without signing or submitting transactions."""
    def __init__(self, connection: sqlite3.Connection):
        self.connection = connection
        self.dedup = DedupStore(connection)

    def ingest(self, bin_lines=(), position_lines=(), observed_at: float = 0.0) -> ReadonlyCycleResult:
        duplicate = 0
        errors = 0
        filtered_bins=[]
        for line in bin_lines:
            try:
                payload=json.loads(line)
                if "error" in payload: continue
                key=observation_key(str(payload["pool_address"]), float(observed_at or 0))
                if self.dedup.claim("bin:"+key, observed_at): filtered_bins.append(line)
                else: duplicate += 1
            except Exception:
                errors += 1
        filtered_positions=[]
        for line in position_lines:
            try:
                payload=json.loads(line)
                if "error" in payload: continue
                key=observation_key(str(payload["pool_address"]), float(observed_at or 0))
                if self.dedup.claim("position:"+key, observed_at): filtered_positions.append(line)
                else: duplicate += 1
            except Exception:
                errors += 1
        bins=positions=0
        try: bins=ingest_bins(self.connection, filtered_bins)
        except Exception: errors += 1
        try: positions=len(ingest_positions(self.connection, filtered_positions))
        except Exception: errors += 1
        return ReadonlyCycleResult(bins, positions, duplicate, errors)
