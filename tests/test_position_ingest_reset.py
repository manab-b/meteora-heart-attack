import json
import sqlite3

from app.collector.position_ingest import ingest_jsonl
from app.storage.migrations import initialize_database
from app.storage.token_quotes import insert_token_quote


def test_reset_or_claim_does_not_create_fee_sol():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_token_quote(connection, pool_address="pool", token_side="x", price_sol=1.0, observed_at=60.0, source="test")
    insert_token_quote(connection, pool_address="pool", token_side="y", price_sol=1.0, observed_at=60.0, source="test")
    base = {
        "source": "meteora-sdk",
        "pool_address": "pool",
        "owner": "owner",
        "active_bin_id": 5,
        "position_address": "position",
        "lower_bin_id": 1,
        "upper_bin_id": 10,
        "total_x_amount_raw": "100",
        "total_y_amount_raw": "100",
        "token_x_decimals": 0,
        "token_y_decimals": 0,
        "total_claimed_fee_x_raw": "0",
        "total_claimed_fee_y_raw": "0",
    }
    first = {**base, "observed_at": "1970-01-01T00:00:00+00:00", "fee_x_raw": "100", "fee_y_raw": "100"}
    reset = {**base, "observed_at": "1970-01-01T00:01:00+00:00", "fee_x_raw": "10", "fee_y_raw": "20"}
    results = ingest_jsonl(connection, [json.dumps(first), json.dumps(reset)])
    assert results[-1]["reset_or_claim"] is True
    assert results[-1]["fee_sol"] is None
