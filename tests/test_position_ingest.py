import json
import sqlite3

from app.collector.position_ingest import ingest_jsonl
from app.storage.migrations import initialize_database


def test_position_jsonl_ingest_derives_fee_delta_and_range_survival():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    rows = [
        {
            "source": "meteora-sdk",
            "observed_at": "2026-01-01T00:00:00+00:00",
            "pool_address": "pool-1",
            "owner": "owner-1",
            "active_bin_id": 105,
            "active_bin_price": "1.0",
            "position_address": "position-1",
            "lower_bin_id": 100,
            "upper_bin_id": 110,
            "total_x_amount_raw": "1000000",
            "total_y_amount_raw": "2000000",
            "fee_x_raw": "100",
            "fee_y_raw": "200",
            "total_claimed_fee_x_raw": "0",
            "total_claimed_fee_y_raw": "0",
        },
        {
            "source": "meteora-sdk",
            "observed_at": "2026-01-01T00:00:30+00:00",
            "pool_address": "pool-1",
            "owner": "owner-1",
            "active_bin_id": 106,
            "active_bin_price": "1.0",
            "position_address": "position-1",
            "lower_bin_id": 100,
            "upper_bin_id": 110,
            "total_x_amount_raw": "1000000",
            "total_y_amount_raw": "2000000",
            "fee_x_raw": "150",
            "fee_y_raw": "260",
            "total_claimed_fee_x_raw": "0",
            "total_claimed_fee_y_raw": "0",
        },
    ]

    results = ingest_jsonl(connection, [json.dumps(row) for row in rows])
    assert results[-1]["fee_x_delta_raw"] == 50
    assert results[-1]["fee_y_delta_raw"] == 60
    assert results[-1]["reset_or_claim"] is False
    assert results[-1]["range_survival_seconds"] == 30
    assert results[-1]["in_range"] is True
