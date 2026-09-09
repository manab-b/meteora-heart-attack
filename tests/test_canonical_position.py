import json
import sqlite3

from app.collector.position_ingest import ingest_jsonl
from app.paper.canonical_position import load_canonical_position_state
from app.storage.bin_liquidity import insert_bin_liquidity
from app.storage.migrations import initialize_database
from app.storage.token_quotes import insert_token_quote


def _payload(observed_at: str, *, fee_x: str = "100", fee_y: str = "200") -> str:
    return json.dumps(
        {
            "source": "meteora-sdk",
            "pool_address": "pool",
            "owner": "owner",
            "active_bin_id": 5,
            "position_address": "position",
            "lower_bin_id": 1,
            "upper_bin_id": 10,
            "total_x_amount_raw": "2000",
            "total_y_amount_raw": "3000",
            "token_x_decimals": 3,
            "token_y_decimals": 3,
            "total_claimed_fee_x_raw": "0",
            "total_claimed_fee_y_raw": "0",
            "observed_at": observed_at,
            "fee_x_raw": fee_x,
            "fee_y_raw": fee_y,
        }
    )


def test_canonical_state_reconstructs_amounts_prices_range_and_mtm():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_token_quote(connection, pool_address="pool", token_side="x", price_sol=2.0, observed_at=60.0, source="test")
    insert_token_quote(connection, pool_address="pool", token_side="y", price_sol=3.0, observed_at=60.0, source="test")
    insert_bin_liquidity(connection, pool_address="pool", bin_id=5, active_bin_id=5, price="1.5", x_amount_raw="100", y_amount_raw="100", observed_at=0.0, source="test")
    insert_bin_liquidity(connection, pool_address="pool", bin_id=5, active_bin_id=5, price="1.6", x_amount_raw="90", y_amount_raw="90", observed_at=60.0, source="test")
    connection.commit()

    ingest_jsonl(
        connection,
        [_payload("1970-01-01T00:00:00+00:00"), _payload("1970-01-01T00:01:00+00:00", fee_x="110", fee_y="220")],
    )

    state = load_canonical_position_state(connection, "position")
    assert state is not None
    assert state.active_bin_id == 5
    assert state.in_range is True
    assert state.x_amount == 2.0
    assert state.y_amount == 3.0
    assert state.x_price_sol == 2.0
    assert state.y_price_sol == 3.0
    assert state.position_value_sol == 13.0
    assert state.eligible_for_mtm is True
    assert state.ineligible_reasons == ()


def test_canonical_state_refuses_stale_price_instead_of_estimating():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_token_quote(connection, pool_address="pool", token_side="x", price_sol=2.0, observed_at=0.0, source="test")
    insert_token_quote(connection, pool_address="pool", token_side="y", price_sol=3.0, observed_at=0.0, source="test")
    connection.commit()

    ingest_jsonl(connection, [_payload("1970-01-01T00:10:00+00:00")])
    state = load_canonical_position_state(connection, "position", max_quote_age_seconds=60.0)

    assert state is not None
    assert state.eligible_for_mtm is False
    assert state.position_value_sol is None
    assert "missing_or_stale_x_price" in state.ineligible_reasons
    assert "missing_or_stale_y_price" in state.ineligible_reasons
