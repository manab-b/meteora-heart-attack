import pytest

from app.metrics.position_pnl import (
    dlmm_pnl_from_canonical_states,
    dlmm_pnl_sol,
    max_drawdown,
    max_drawdown_pct,
    position_pnl,
    position_value_usd,
)
from app.paper.canonical_position import CanonicalPositionState


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
    assert result.hodl_value_usd == 220
    assert result.current_value_usd == 200
    assert result.il_pct == pytest.approx((200 / 220 - 1.0) * 100.0)
    assert result.net_return_pct == pytest.approx(5.0)


def test_negative_fees_are_rejected():
    with pytest.raises(ValueError):
        position_pnl(1, 1, 1, 1, 1, 1, 1, 1, fees_usd=-1)


def test_dlmm_pnl_sol_separates_hodl_il_and_fees():
    result = dlmm_pnl_sol(
        entry_x_amount=1.0,
        entry_y_amount=1.0,
        current_x_amount=0.5,
        current_y_amount=1.4,
        entry_x_sol_price=2.0,
        entry_y_sol_price=1.0,
        current_x_sol_price=3.0,
        current_y_sol_price=1.0,
        fees_sol=0.2,
    )
    assert result.entry_value_sol == pytest.approx(3.0)
    assert result.current_value_sol == pytest.approx(2.9)
    assert result.hodl_value_sol == pytest.approx(4.0)
    assert result.fees_sol == pytest.approx(0.2)
    assert result.il_pct == pytest.approx((2.9 / 4.0 - 1.0) * 100.0)
    assert result.net_pnl_sol == pytest.approx(0.1)
    assert result.net_return_pct == pytest.approx(0.1 / 3.0 * 100.0)


def _canonical(x_amount, y_amount, x_price, y_price, eligible=True):
    return CanonicalPositionState(
        position_address="position",
        pool_address="pool",
        observed_at=60.0,
        active_bin_id=5,
        lower_bin_id=1,
        upper_bin_id=10,
        in_range=True,
        range_survival_seconds=60.0,
        drain_score=0.1,
        x_amount=x_amount,
        y_amount=y_amount,
        x_price_sol=x_price,
        y_price_sol=y_price,
        x_decimals=3,
        y_decimals=3,
        fee_x_delta_raw=10,
        fee_y_delta_raw=20,
        fee_sol=0.1,
        reset_or_claim=False,
        position_value_sol=None if not eligible else x_amount * x_price + y_amount * y_price,
        eligible_for_mtm=eligible,
        ineligible_reasons=() if eligible else ("missing_or_stale_x_price",),
    )


def test_dlmm_pnl_from_canonical_states_uses_observed_inventory_and_prices():
    entry = _canonical(1.0, 1.0, 2.0, 1.0)
    current = _canonical(0.5, 1.4, 3.0, 1.0)
    result = dlmm_pnl_from_canonical_states(entry, current, fees_sol=0.2)
    assert result.current_value_sol == pytest.approx(2.9)
    assert result.hodl_value_sol == pytest.approx(4.0)
    assert result.net_pnl_sol == pytest.approx(0.1)


def test_dlmm_pnl_from_canonical_states_rejects_ineligible_state():
    entry = _canonical(1.0, 1.0, 2.0, 1.0)
    current = _canonical(0.5, 1.4, 3.0, 1.0, eligible=False)
    with pytest.raises(ValueError):
        dlmm_pnl_from_canonical_states(entry, current, fees_sol=0.2)


def test_dlmm_pnl_rejects_invalid_prices_and_fees():
    with pytest.raises(ValueError):
        dlmm_pnl_sol(1, 1, 1, 1, 0, 1, 1, 1)
    with pytest.raises(ValueError):
        dlmm_pnl_sol(1, 1, 1, 1, 1, 1, 1, 1, fees_sol=-0.1)


def test_max_drawdown_uses_peak_to_trough_values():
    assert max_drawdown([10, 12, 9, 11, 7, 8]) == pytest.approx(5.0)
    assert max_drawdown_pct([10, 12, 9, 11, 7, 8]) == pytest.approx(5 / 12 * 100.0)
    assert max_drawdown([]) == 0.0


def test_max_drawdown_rejects_invalid_equity():
    with pytest.raises(ValueError):
        max_drawdown([10, -1])
    with pytest.raises(ValueError):
        max_drawdown_pct([0, 1])
