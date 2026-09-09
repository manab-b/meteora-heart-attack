import sqlite3

from app.collector.bin_snapshot import persist_bin_observations
from app.collector.pool_state import BinLiquidityObservation
from app.storage.migrations import initialize_database


def _row(ts, x, y):
    return BinLiquidityObservation("POOL", 10, 10, "1.0", str(x), str(y), ts)


def test_bin_snapshot_creates_drain_only_after_previous_snapshot():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    first = "2026-09-09T12:00:00+00:00"
    second = "2026-09-09T12:01:00+00:00"

    assert persist_bin_observations(connection, [_row(first, 100, 100)]) == 1
    assert connection.execute("SELECT COUNT(*) FROM bin_drain_events").fetchone()[0] == 0

    assert persist_bin_observations(connection, [_row(second, 50, 100)]) == 1
    assert connection.execute("SELECT COUNT(*) FROM bin_drain_events").fetchone()[0] == 1
