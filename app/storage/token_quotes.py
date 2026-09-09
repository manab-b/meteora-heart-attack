from __future__ import annotations

import sqlite3


def init_token_quote_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS token_quotes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pool_address TEXT NOT NULL,
            token_side TEXT NOT NULL CHECK(token_side IN ('x', 'y')),
            token_mint TEXT,
            price_sol REAL NOT NULL,
            observed_at REAL NOT NULL,
            source TEXT NOT NULL
        );
        CREATE INDEX IF NOT EXISTS idx_token_quotes_lookup
        ON token_quotes(pool_address, token_side, observed_at);
        """
    )


def insert_token_quote(
    connection: sqlite3.Connection,
    *,
    pool_address: str,
    token_side: str,
    price_sol: float,
    observed_at: float,
    source: str,
    token_mint: str | None = None,
) -> None:
    if token_side not in {"x", "y"}:
        raise ValueError("token_side must be 'x' or 'y'")
    if price_sol < 0:
        raise ValueError("price_sol must be non-negative")
    connection.execute(
        """INSERT INTO token_quotes
        (pool_address, token_side, token_mint, price_sol, observed_at, source)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (pool_address, token_side, token_mint, price_sol, observed_at, source),
    )


def latest_token_quote(
    connection: sqlite3.Connection,
    *,
    pool_address: str,
    token_side: str,
    observed_at: float,
    max_age_seconds: float,
) -> tuple[float, float, str] | None:
    if token_side not in {"x", "y"}:
        raise ValueError("token_side must be 'x' or 'y'")
    row = connection.execute(
        """SELECT price_sol, observed_at, source
        FROM token_quotes
        WHERE pool_address = ? AND token_side = ? AND observed_at <= ?
        ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (pool_address, token_side, observed_at),
    ).fetchone()
    if row is None:
        return None
    age = observed_at - float(row[1])
    if age < 0 or age > max_age_seconds:
        return None
    return float(row[0]), float(row[1]), str(row[2])
