import sqlite3

from app.runtime.readonly_cycle import ReadonlyCycle
from app.storage.bin_drain import init_bin_drain_schema
from app.storage.bin_liquidity import init_bin_liquidity_schema
from app.storage.raw import init_raw_schema


def _connection():
    conn = sqlite3.connect(":memory:")
    init_raw_schema(conn)
    init_bin_liquidity_schema(conn)
    init_bin_drain_schema(conn)
    return conn


def test_readonly_cycle_keeps_distinct_bins_at_same_timestamp():
    conn = _connection()
    cycle = ReadonlyCycle(conn)
    timestamp = "2026-09-10T00:00:00Z"
    lines = [
        '{"pool_address":"P","observed_at":"2026-09-10T00:00:00Z","bin_id":1,"active_bin_id":1,"price":"1","x_amount_raw":"10","y_amount_raw":"20"}',
        '{"pool_address":"P","observed_at":"2026-09-10T00:00:00Z","bin_id":2,"active_bin_id":1,"price":"1.01","x_amount_raw":"30","y_amount_raw":"40"}',
    ]
    first = cycle.ingest(lines)
    second = cycle.ingest(lines)
    assert first.bin_observations == 2
    assert first.duplicate_records == 0
    assert second.bin_observations == 0
    assert second.duplicate_records == 2
    assert conn.execute("SELECT COUNT(*) FROM bin_liquidity_snapshots").fetchone()[0] == 2


def test_readonly_cycle_rejects_malformed_records_without_stopping_valid_records():
    conn = _connection()
    cycle = ReadonlyCycle(conn)
    valid = '{"pool_address":"P","observed_at":"2026-09-10T00:00:00Z","bin_id":1,"active_bin_id":1,"price":"1","x_amount_raw":"10","y_amount_raw":"20"}'
    result = cycle.ingest(["not-json", valid])
    assert result.bin_observations == 1
    assert result.errors == 1
