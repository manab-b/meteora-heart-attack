import sqlite3

from app.collector.bin_ingest import ingest_jsonl
from app.storage.migrations import initialize_database


def test_bin_ingest_persists_consecutive_drain_event():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    lines = [
        '{"observed_at":"2026-01-01T00:00:00Z","pool_address":"pool","bin_id":9,"active_bin_id":10,"price":"1","x_amount_raw":"100","y_amount_raw":"100"}',
        '{"observed_at":"2026-01-01T00:00:30Z","pool_address":"pool","bin_id":9,"active_bin_id":10,"price":"1","x_amount_raw":"50","y_amount_raw":"100"}',
    ]
    assert ingest_jsonl(connection, lines) == 2
    row = connection.execute(
        "SELECT elapsed_seconds, depletion_ratio, score, active_bin_moved FROM bin_drain_events"
    ).fetchone()
    assert row == (30.0, 0.25, 0.25, 0)


def test_first_bin_observation_has_no_drain_event():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    lines = [
        '{"observed_at":"2026-01-01T00:00:00Z","pool_address":"pool","bin_id":9,"active_bin_id":10,"price":"1","x_amount_raw":"100","y_amount_raw":"100"}'
    ]
    ingest_jsonl(connection, lines)
    count = connection.execute("SELECT COUNT(*) FROM bin_drain_events").fetchone()[0]
    assert count == 0
