import json
import sqlite3
from datetime import datetime, timezone
from app.runtime.readonly_cycle import ReadonlyCycle
from app.storage.migrations import initialize_database

def _line(ts):
    return json.dumps({"observed_at":ts,"pool_address":"POOL","active_bin_id":10,"bin_id":10,"price":"1","x_amount_raw":"100","y_amount_raw":"200"})

def test_bin_duplicate_is_exactly_one_observation():
    conn=sqlite3.connect(":memory:"); initialize_database(conn)
    ts=datetime.now(timezone.utc).isoformat().replace("+00:00","Z")
    cycle=ReadonlyCycle(conn)
    first=cycle.ingest([_line(ts)])
    second=cycle.ingest([_line(ts)])
    assert first.bin_observations==1
    assert second.bin_observations==0
    assert second.duplicate_records==1

def test_same_pool_different_timestamp_is_not_duplicate():
    conn=sqlite3.connect(":memory:"); initialize_database(conn)
    cycle=ReadonlyCycle(conn)
    a="2026-01-01T00:00:00Z"; b="2026-01-01T00:00:30Z"
    assert cycle.ingest([_line(a)]).bin_observations==1
    assert cycle.ingest([_line(b)]).bin_observations==1
