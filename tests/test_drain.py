import pytest

from app.metrics.drain import DrainObservation, liquidity_drain_rate, liquidity_drain_score


def test_liquidity_drain_rate_is_per_minute():
    assert liquidity_drain_rate(1000.0, 900.0, 30.0) == pytest.approx(0.2)


def test_liquidity_increase_is_not_drain():
    assert liquidity_drain_rate(1000.0, 1100.0, 30.0) == 0.0


def test_invalid_elapsed_is_rejected():
    with pytest.raises(ValueError):
        liquidity_drain_rate(1000.0, 900.0, 0.0)


def test_active_bin_migration_discount():
    normal = liquidity_drain_score(1000, 500)
    migrated = liquidity_drain_score(1000, 500, active_bin_moved=True)
    assert normal == 0.5
    assert migrated == pytest.approx(0.175)


def test_drain_observation_rate():
    observation = DrainObservation(1000, 800, 30, active_bin_moved=False)
    assert observation.drain_score == pytest.approx(0.2)
    assert observation.drain_rate_per_minute == pytest.approx(0.4)
    assert liquidity_drain_rate(1000, 800, 30) == pytest.approx(0.4)
