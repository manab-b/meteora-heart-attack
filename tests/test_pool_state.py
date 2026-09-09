import pytest

from app.collector.pool_state import normalize_bin_liquidity


def test_normalize_bins_keeps_raw_amounts_as_strings():
    rows = normalize_bin_liquidity(
        pool_address="POOL",
        payload={
            "activeBin": 42,
            "bins": [
                {"binId": 41, "xAmount": "00123", "yAmount": "00456", "price": "1.25"},
                {"binId": 42, "xAmount": 0, "yAmount": 789, "pricePerToken": "1.30"},
            ],
        },
        observed_at="2026-09-09T12:00:00+00:00",
    )
    assert rows[0].bin_id == 41
    assert rows[0].active_bin_id == 42
    assert rows[0].x_amount_raw == "00123"
    assert rows[0].y_amount_raw == "00456"
    assert rows[1].x_amount_raw == "0"
    assert rows[1].y_amount_raw == "789"


def test_normalize_bins_rejects_missing_active_bin():
    with pytest.raises(ValueError, match="active bin"):
        normalize_bin_liquidity(
            pool_address="POOL",
            payload={"bins": []},
            observed_at="2026-09-09T12:00:00+00:00",
        )
