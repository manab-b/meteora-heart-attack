from app.collector.pools import normalize_pool


def test_normalizes_pool_metrics():
    pool = normalize_pool({
        "address": "POOL",
        "current_price": 1.25,
        "tvl": 12345,
        "volume": {"24h": 45678},
        "fees": {"24h": 321.5},
        "dynamic_fee_pct": 0.12,
        "pool_config": {
            "bin_step": 25,
            "base_fee_pct": 0.01,
            "max_fee_pct": 2.0,
            "protocol_fee_pct": 0.1,
        },
    })
    assert pool.address == "POOL"
    assert pool.bin_step == 25
    assert pool.volume_24h_usd == 45678.0
    assert pool.fees_24h_usd == 321.5


def test_missing_optional_fields_do_not_become_fake_values():
    pool = normalize_pool({"address": "POOL"})
    assert pool.address == "POOL"
    assert pool.current_price is None
    assert pool.bin_step is None
