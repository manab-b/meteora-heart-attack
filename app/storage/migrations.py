from __future__ import annotations

import sqlite3

from app.positions.store import init_position_schema
from app.storage.bin_drain import init_bin_drain_schema
from app.storage.bin_liquidity import init_bin_liquidity_schema
from app.storage.fee_deltas import init_fee_delta_schema
from app.storage.observations import init_observation_schema
from app.storage.paper_trades import init_paper_trade_schema
from app.storage.position_analytics import init_position_analytics_schema
from app.storage.raw import init_raw_schema
from app.storage.token_quotes import init_token_quote_schema


def initialize_database(connection: sqlite3.Connection) -> None:
    init_observation_schema(connection)
    init_position_schema(connection)
    init_fee_delta_schema(connection)
    init_position_analytics_schema(connection)
    init_raw_schema(connection)
    init_token_quote_schema(connection)
    init_bin_liquidity_schema(connection)
    init_bin_drain_schema(connection)
    init_paper_trade_schema(connection)
