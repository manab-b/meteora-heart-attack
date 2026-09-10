import json
import sqlite3

from app.collector.position_ingest import WSOL_MINT, ingest_jsonl
from app.storage.migrations import initialize_database
from app.storage.token_quotes import insert_token_quote, latest_token_quote


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
    assert results[-1]["fee_sol"] is None
    assert results[-1]["reset_or_claim"] is False
    assert results[-1]["range_survival_seconds"] == 30
    assert results[-1]["in_range"] is True


def test_position_ingest_values_fee_when_fresh_quotes_and_decimals_exist():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_token_quote(
        connection,
        pool_address="pool-1",
        token_side="x",
        price_sol=1.0,
        observed_at=30.0,
        source="quote-test",
    )
    insert_token_quote(
        connection,
        pool_address="pool-1",
        token_side="y",
        price_sol=2.0,
        observed_at=30.0,
        source="quote-test",
    )
    rows = [
        {
            "source": "meteora-sdk",
            "observed_at": "1970-01-01T00:00:00+00:00",
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
            "token_x_decimals": 6,
            "token_y_decimals": 6,
        },
        {
            "source": "meteora-sdk",
            "observed_at": "1970-01-01T00:00:30+00:00",
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
            "token_x_decimals": 6,
            "token_y_decimals": 6,
        },
    ]
    results = ingest_jsonl(connection, [json.dumps(row) for row in rows])
    assert results[-1]["fee_sol"] == 0.00017


def test_sol_pair_active_bin_price_creates_authoritative_quotes_and_values_fee():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    rows = [
        {
            "source": "meteora-sdk",
            "observed_at": "1970-01-01T00:00:00+00:00",
            "pool_address": "sol-pool",
            "owner": "owner-1",
            "active_bin_id": 105,
            "active_bin_price": "raw",
            "active_bin_price_ui": 0.0005,
            "position_address": "position-sol",
            "lower_bin_id": 100,
            "upper_bin_id": 110,
            "total_x_amount_raw": "1000000000",
            "total_y_amount_raw": "2000000",
            "fee_x_raw": "1000000",
            "fee_y_raw": "2000",
            "total_claimed_fee_x_raw": "0",
            "total_claimed_fee_y_raw": "0",
            "token_x_mint": "TokenX",
            "token_y_mint": WSOL_MINT,
            "token_x_decimals": 9,
            "token_y_decimals": 9,
        },
        {
            "source": "meteora-sdk",
            "observed_at": "1970-01-01T00:00:30+00:00",
            "pool_address": "sol-pool",
            "owner": "owner-1",
            "active_bin_id": 106,
            "active_bin_price": "raw",
            "active_bin_price_ui": 0.0005,
            "position_address": "position-sol",
            "lower_bin_id": 100,
            "upper_bin_id": 110,
            "total_x_amount_raw": "1000000000",
            "total_y_amount_raw": "2000000",
            "fee_x_raw": "1001000",
            "fee_y_raw": "3000",
            "total_claimed_fee_x_raw": "0",
            "total_claimed_fee_y_raw": "0",
            "token_x_mint": "TokenX",
            "token_y_mint": WSOL_MINT,
            "token_x_decimals": 9,
            "token_y_decimals": 9,
        },
    ]

    results = ingest_jsonl(connection, [json.dumps(row) for row in rows])
    assert results[-1]["fee_x_delta_raw"] == 1000
    assert results[-1]["fee_y_delta_raw"] == 1000
    assert results[-1]["fee_sol"] == 0.0000015

    x_quote = latest_token_quote(
        connection,
        pool_address="sol-pool",
        token_side="x",
        observed_at=30.0,
        max_age_seconds=1.0,
    )
    y_quote = latest_token_quote(
        connection,
        pool_address="sol-pool",
        token_side="y",
        observed_at=30.0,
        max_age_seconds=1.0,
    )
    assert x_quote is not None and x_quote[0] == 0.0005
    assert y_quote is not None and y_quote[0] == 1.0
