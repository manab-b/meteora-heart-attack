import pytest

from app.metrics.position_pnl import position_pnl, position_value_usd


def test_position_value_usd():
    value = position_value_usd(2, 100, 10, 1)
    assert value.value_usd == 120


def test_position_il_is_separate_from_fees():
    result = position_pnl(
        1,
        100,
        0.5,
        140,
        100,
        1,
        120,
        1,
        fees_usd=10,
    )
    # HODL keeps the original token quantities while repricing them at current prices.
    assert result.hodl_value_usd == 220
    assert result.current_value_usd == 200
    assert result.il_pct == pytest.approx((200 / 220 - 1.0) * 100.0)
    assert result.net_return_pct == pytest.approx(5.0)


def test_negative_fees_are_rejected():
    with pytest.raises(ValueError):
        position_pnl(1, 1, 1, 1, 1, 1, 1, 1, fees_usd=-1)
