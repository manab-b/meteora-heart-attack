from __future__ import annotations

import sqlite3

SCHEMA_VERSION = 2


def migrate(conn: sqlite3.Connection) -> None:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_meta(version INTEGER NOT NULL)")
    current = int(conn.execute("SELECT COALESCE(MAX(version),0) FROM schema_meta").fetchone()[0])
    if current < 1:
        from app.storage.equity import ensure_equity
        from app.storage.paper_trades import ensure_paper_trades
        from app.research.results import ensure_results
        from app.storage.raw_observations import ensure_raw_observations
        ensure_raw_observations(conn)
        ensure_paper_trades(conn)
        ensure_equity(conn)
        ensure_results(conn)
        conn.execute("INSERT INTO schema_meta(version) VALUES(1)")
        conn.commit()


def initialize_database(connection: sqlite3.Connection) -> None:
    """Initialize every schema used by the current paper/read-only pipeline."""
    from app.storage.bin_drain import init_bin_drain_schema
    from app.storage.bin_liquidity import init_bin_liquidity_schema
    from app.storage.observations import init_observation_schema
    from app.storage.position_analytics import init_position_analytics_schema
    from app.storage.raw import init_raw_schema
    from app.storage.token_quotes import init_token_quote_schema
    from app.storage.paper_trades import ensure_paper_trades

    migrate(connection)
    init_observation_schema(connection)
    init_raw_schema(connection)
    init_bin_liquidity_schema(connection)
    init_bin_drain_schema(connection)
    init_position_analytics_schema(connection)
    init_token_quote_schema(connection)

    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS position_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_address TEXT NOT NULL,
            owner TEXT NOT NULL,
            pool_address TEXT NOT NULL,
            lower_bin_id INTEGER,
            upper_bin_id INTEGER,
            deposited_x TEXT NOT NULL,
            deposited_y TEXT NOT NULL,
            unclaimed_fee_x TEXT NOT NULL,
            unclaimed_fee_y TEXT NOT NULL,
            observed_at TEXT NOT NULL,
            source TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_position_snapshots_time
        ON position_snapshots(position_address, observed_at);
        """
    )
    ensure_paper_trades(connection)
    connection.commit()
