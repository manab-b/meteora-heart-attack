import pytest

from app.valuation.model import fee_sol_value, raw_to_units, token_usd_value


def test_raw_to_units():
    assert raw_to_units("123456", 6) == pytest.approx(0.123456)


def test_token_usd_value():
    assert token_usd_value(2_000_000, 6, 3.5) == pytest.approx(7.0)


def test_fee_sol_value_requires_real_prices():
    with pytest.raises(ValueError):
        fee_sol_value(1_000_000, 2_000_000, 6, 6, None, 0.01)


def test_fee_sol_value():
    value = fee_sol_value(1_000_000, 2_000_000, 6, 6, 0.01, 0.02)
    assert value == pytest.approx(0.05)
