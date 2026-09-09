import pytest

from app.collector.pool_snapshot import normalize_pool_snapshot


def test_normalize_pool_snapshot_preserves_missing_values():
    payload = {
        "address": "pool-1",
        "current_price": "1.25",
        "tvl": 250000,
        "volume_24h": 900000,
        "fees_24h": 1800,
        "dynamic_fee_pct": "0.12",
        "pool_config": {"bin_step": 25},
        "token_x": {"symbol": "SOL", "price": 180},
        "token_y": {"symbol": "USDC", "price": 1},
        "blacklisted": False,
    }

    snapshot = normalize_pool_snapshot(payload, observed_at=123.0)

    assert snapshot.address == "pool-1"
    assert snapshot.current_price == pytest.approx(1.25)
    assert snapshot.tvl_usd == pytest.approx(250000)
    assert snapshot.volume_24h_usd == pytest.approx(900000)
    assert snapshot.fee_24h_usd == pytest.approx(1800)
    assert snapshot.dynamic_fee_pct == pytest.approx(0.12)
    assert snapshot.bin_step == 25
    assert snapshot.token_x_symbol == "SOL"
    assert snapshot.token_x_price_usd == pytest.approx(180)
    assert snapshot.volume_5m_usd is None
    assert snapshot.fee_5m_usd is None


def test_pool_address_is_required():
    with pytest.raises(ValueError):
        normalize_pool_snapshot({"current_price": 1.0}, observed_at=123.0)
