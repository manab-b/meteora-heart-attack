import sqlite3

import pytest

from app.positions.analytics import (
    consecutive_range_survival,
    position_fee_delta,
    range_state,
)
from app.storage.position_analytics import (
    init_position_analytics_schema,
    insert_position_analytics,
)


def test_bin_range_state_and_survival():
    assert range_state(105, 100, 110).in_range
    assert consecutive_range_survival(30, 30, 105, 100, 110) == 60
    assert consecutive_range_survival(60, 30, 111, 100, 110) == 0


def test_fee_delta_handles_claim_reset():
    dx, dy, reset = position_fee_delta("100", "200", "150", "260")
    assert dx == 50
    assert dy == 60
    assert reset is False

    dx, dy, reset = position_fee_delta("100", "200", "90", "250")
    assert dx == 0
    assert dy == 50
    assert reset is True


def test_invalid_bin_range_is_rejected():
    with pytest.raises(ValueError):
        range_state(100, 110, 100)


def test_position_analytics_storage():
    connection = sqlite3.connect(":memory:")
    init_position_analytics_schema(connection)
    insert_position_analytics(
        connection,
        position_address="position-1",
        pool_address="pool-1",
        observed_at=100.0,
        active_bin_id=105,
        lower_bin_id=100,
        upper_bin_id=110,
        in_range=True,
        range_survival_seconds=60.0,
        fee_x_delta_raw=50,
        fee_y_delta_raw=60,
        reset_or_claim=False,
        fee_sol=0.01,
        source="test",
    )
    row = connection.execute(
        "SELECT position_address, in_range, fee_x_delta_raw, fee_y_delta_raw FROM position_analytics"
    ).fetchone()
    assert row == ("position-1", 1, "50", "60")
