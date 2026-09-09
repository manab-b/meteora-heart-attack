import sqlite3

import pytest

from app.storage.migrations import initialize_database
from app.storage.token_quotes import insert_token_quote, latest_token_quote


def test_latest_quote_is_fresh_and_time_ordered():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_token_quote(
        connection,
        pool_address="pool-1",
        token_side="x",
        price_sol=0.5,
        observed_at=100.0,
        source="test",
    )
    insert_token_quote(
        connection,
        pool_address="pool-1",
        token_side="x",
        price_sol=0.7,
        observed_at=110.0,
        source="test-new",
    )
    quote = latest_token_quote(
        connection,
        pool_address="pool-1",
        token_side="x",
        observed_at=115.0,
        max_age_seconds=10.0,
    )
    assert quote == (0.7, 110.0, "test-new")


def test_stale_quote_is_not_used():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_token_quote(
        connection,
        pool_address="pool-1",
        token_side="y",
        price_sol=2.0,
        observed_at=100.0,
        source="test",
    )
    assert latest_token_quote(
        connection,
        pool_address="pool-1",
        token_side="y",
        observed_at=120.0,
        max_age_seconds=10.0,
    ) is None


def test_invalid_side_is_rejected():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    with pytest.raises(ValueError):
        insert_token_quote(
            connection,
            pool_address="pool-1",
            token_side="z",
            price_sol=1.0,
            observed_at=100.0,
            source="test",
        )
