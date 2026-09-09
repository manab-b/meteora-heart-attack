import pytest

from app.metrics.drain import liquidity_drain_rate


def test_liquidity_drain_rate_is_per_minute():
    assert liquidity_drain_rate(1000.0, 900.0, 30.0) == pytest.approx(0.2)


def test_liquidity_increase_is_not_drain():
    assert liquidity_drain_rate(1000.0, 1100.0, 30.0) == 0.0


def test_invalid_elapsed_is_rejected():
    with pytest.raises(ValueError):
        liquidity_drain_rate(1000.0, 900.0, 0.0)
