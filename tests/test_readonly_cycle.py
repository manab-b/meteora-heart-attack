from app.runtime.readonly_cycle import ReadonlyCycle
import sqlite3

def test_readonly_cycle_deduplicates_invalid_records():
    conn=sqlite3.connect(":memory:")
    # Dedup happens before schema-dependent ingestion; malformed records are rejected safely.
    cycle=ReadonlyCycle(conn)
    payload='{"pool_address":"P","observed_at":"2026-09-10T00:00:00Z","bin_id":1,"active_bin_id":1,"price":"1","x_amount_raw":"10","y_amount_raw":"20"}'
    first=cycle.ingest([payload],[],1.0)
    second=cycle.ingest([payload],[],1.0)
    assert first.duplicate_records == 0
    assert second.duplicate_records == 1
