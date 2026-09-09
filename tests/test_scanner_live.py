import sqlite3

from app.scanner.live import scan_paper_opportunities
from app.storage.bin_drain import init_bin_drain_schema
from app.storage.observations import init_observation_schema


def test_scanner_uses_latest_observation_and_bin_drain():
    connection = sqlite3.connect(":memory:")
    init_observation_schema(connection)
    init_bin_drain_schema(connection)

    connection.execute(
        """INSERT INTO observations
        (pool_address, bins, timestamp, price, volume_usd, fee_velocity_sol_min,
         drain_score, range_survival_seconds, in_range)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("pool-a", 10, 100.0, 1.0, 1_000_000, 0.2, 0.0, 300.0, 1),
    )
    connection.execute(
        """INSERT INTO observations
        (pool_address, bins, timestamp, price, volume_usd, fee_velocity_sol_min,
         drain_score, range_survival_seconds, in_range)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("pool-b", 10, 100.0, 1.0, 2_000_000, 0.3, 0.0, 300.0, 0),
    )
    connection.execute(
        """INSERT INTO bin_drain_events
        (pool_address, bin_id, previous_observed_at, observed_at, elapsed_seconds,
         active_bin_moved, depletion_ratio, score, source)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        ("pool-a", 1, 0.0, 100.0, 100.0, 0, 0.1, 0.1, "test"),
    )
    connection.commit()

    result = scan_paper_opportunities(connection, ["pool-a", "pool-b"])
    assert [candidate.pool_address for candidate in result] == ["pool-a"]
    assert result[0].drain_score == 0.1
