import sqlite3

import pytest

from app.positions.fee_delta import fee_delta, fee_velocity_from_delta
from app.storage.fee_deltas import (
    init_fee_delta_schema,
    insert_fee_observation,
    latest_fee_observation,
)


def test_positive_fee_delta_and_velocity():
    delta = fee_delta("position-1", 1.0, 1.25, 100.0)
    assert delta.raw_delta_sol == pytest.approx(0.25)
    assert delta.accrued_fee_sol == pytest.approx(0.25)
    assert delta.reset_or_claim is False
    assert fee_velocity_from_delta(delta, 30.0) == pytest.approx(0.5)


def test_negative_delta_is_reset_or_claim():
    delta = fee_delta("position-1", 2.0, 0.5, 100.0)
    assert delta.raw_delta_sol == pytest.approx(-1.5)
    assert delta.accrued_fee_sol == 0.0
    assert delta.reset_or_claim is True


def test_negative_fee_input_is_rejected():
    with pytest.raises(ValueError):
        fee_delta("position-1", -1.0, 0.5, 100.0)

    with pytest.raises(ValueError):
        fee_delta("position-1", 1.0, -0.5, 100.0)


def test_zero_or_negative_elapsed_time_has_zero_velocity():
    delta = fee_delta("position-1", 1.0, 2.0, 100.0)
    assert fee_velocity_from_delta(delta, 0.0) == 0.0
    assert fee_velocity_from_delta(delta, -1.0) == 0.0


def test_fee_observation_storage_returns_latest_row():
    connection = sqlite3.connect(":memory:")
    init_fee_delta_schema(connection)

    insert_fee_observation(
        connection,
        position_address="position-1",
        pool_address="pool-1",
        observed_at=100.0,
        fee_x=0.1,
        fee_y=0.2,
        fee_sol=0.3,
        source="test",
    )
    insert_fee_observation(
        connection,
        position_address="position-1",
        pool_address="pool-1",
        observed_at=130.0,
        fee_x=0.2,
        fee_y=0.4,
        fee_sol=0.6,
        source="test",
    )

    latest = latest_fee_observation(connection, "position-1")
    assert latest is not None
    assert latest["observed_at"] == 130.0
    assert latest["fee_sol"] == pytest.approx(0.6)


def test_fee_observation_rejects_negative_values():
    connection = sqlite3.connect(":memory:")
    init_fee_delta_schema(connection)

    with pytest.raises(ValueError):
        insert_fee_observation(
            connection,
            position_address="position-1",
            pool_address="pool-1",
            observed_at=100.0,
            fee_x=-0.1,
            fee_y=0.2,
            fee_sol=0.3,
            source="test",
        )
