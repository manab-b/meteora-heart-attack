import sqlite3

from app.storage.bin_drain import init_bin_drain_schema
from app.storage.pool_drain import latest_pool_drain


def test_latest_pool_drain_reads_recent_events():
    connection = sqlite3.connect(":memory:")
    init_bin_drain_schema(connection)
    connection.execute(
        """
        INSERT INTO bin_drain_events
        (pool_address, bin_id, previous_observed_at, observed_at, elapsed_seconds,
         active_bin_moved, depletion_ratio, score, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("pool", 1, 0.0, 100.0, 100.0, 0, 0.8, 0.8, "test"),
    )
    connection.execute(
        """
        INSERT INTO bin_drain_events
        (pool_address, bin_id, previous_observed_at, observed_at, elapsed_seconds,
         active_bin_moved, depletion_ratio, score, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("pool", 2, 0.0, 100.0, 100.0, 1, 0.4, 0.14, "test"),
    )
    connection.commit()

    result = latest_pool_drain(connection, "pool", lookback_seconds=60)
    assert result.event_count == 2
    assert result.max_bin_score == 0.8
    assert result.score == 0.47
    assert result.active_bin_migration_events == 1
