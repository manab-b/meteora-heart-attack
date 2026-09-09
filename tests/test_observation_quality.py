import sqlite3

from app.data_quality.observations import ObservationQualityConfig, assess_observation_quality
from app.storage.migrations import initialize_database
from app.storage.observations import insert_observation


def test_quality_rejects_sparse_pool():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_observation(connection, "pool", 3, 100.0, 1.0, 100000.0, 0.02, 0.1, 60.0, True)

    quality = assess_observation_quality(connection, "pool")

    assert not quality.ok
    assert "INSUFFICIENT_OBSERVATIONS" in quality.reasons


def test_quality_rejects_large_timestamp_gap_and_out_of_range():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    for timestamp in (1000.0, 900.0, 800.0, 700.0, 100.0):
        insert_observation(connection, "pool", 3, timestamp, 1.0, 100000.0, 0.02, 0.1, 60.0, timestamp != 1000.0)

    quality = assess_observation_quality(
        connection,
        "pool",
        config=ObservationQualityConfig(min_observations=5, max_gap_seconds=300.0),
    )

    assert not quality.ok
    assert "TIMESTAMP_GAP" in quality.reasons
    assert "LATEST_OUT_OF_RANGE" in quality.reasons


def test_quality_accepts_dense_valid_history():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    for timestamp in (500.0, 440.0, 380.0, 320.0, 260.0):
        insert_observation(connection, "pool", 3, timestamp, 1.0, 100000.0, 0.02, 0.1, 60.0, True)

    quality = assess_observation_quality(connection, "pool")

    assert quality.ok
    assert quality.count == 5
    assert quality.max_gap_seconds == 60.0
