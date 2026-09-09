from app.runtime.meteora_jsonl_adapter import adapt_bin_record, adapt_jsonl


def test_adapt_bin_record_preserves_raw_liquidity():
    row = adapt_bin_record({
        "pool_address": "POOL",
        "observed_at": 100.0,
        "price": 12.5,
        "active_bin_id": 7,
        "bin_id": 6,
        "x_amount_raw": "123",
        "y_amount_raw": "456",
    })
    assert row.pool_address == "POOL"
    assert row.x_amount_raw == 123
    assert row.y_amount_raw == 456


def test_adapt_jsonl_skips_sdk_error_records():
    rows = adapt_jsonl([
        {"error": "rpc unavailable"},
        {"pool_address": "P", "observed_at": 1, "price": 1, "active_bin_id": 1,
         "bin_id": 1, "x_amount_raw": "1", "y_amount_raw": "2"},
    ])
    assert len(rows) == 1
