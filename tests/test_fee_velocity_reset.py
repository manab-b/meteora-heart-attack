import pytest

from app.metrics.fee_velocity import FeeObservation, fee_velocity_per_minute


def test_positive_fee_delta():
    a = FeeObservation(0, 0.10)
    b = FeeObservation(60, 0.13)
    assert fee_velocity_per_minute(a, b) == pytest.approx(0.03)


def test_claim_reset_does_not_create_negative_velocity():
    a = FeeObservation(0, 0.13)
    b = FeeObservation(60, 0.02)
    assert fee_velocity_per_minute(a, b) == 0.0
