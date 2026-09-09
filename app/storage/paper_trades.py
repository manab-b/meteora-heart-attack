from __future__ import annotations

import sqlite3
from typing import Any


_CREATE_POSITIONS = """
CREATE TABLE IF NOT EXISTS paper_positions (
    position_id TEXT PRIMARY KEY,
    pool_address TEXT NOT NULL,
    entry_time REAL NOT NULL,
    entry_price REAL NOT NULL,
    min_price REAL NOT NULL,
    max_price REAL NOT NULL,
    deposit_sol REAL NOT NULL,
    fee_sol REAL NOT NULL DEFAULT 0,
    claimed_sol REAL NOT NULL DEFAULT 0,
    status TEXT NOT NULL,
    out_of_range_since REAL,
    entry_x_amount REAL,
    entry_y_amount REAL,
    current_x_amount REAL,
    current_y_amount REAL,
    entry_x_price_usd REAL,
    entry_y_price_usd REAL,
    current_x_price_usd REAL,
    current_y_price_usd REAL
)
"""

_CREATE_EVENTS = """
CREATE TABLE IF NOT EXISTS paper_position_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp REAL NOT NULL,
    action TEXT NOT NULL,
    position_id TEXT NOT NULL,
    pool_address TEXT NOT NULL,
    price REAL NOT NULL,
    fee_sol REAL NOT NULL,
    claimed_sol REAL NOT NULL,
    status TEXT NOT NULL,
    UNIQUE(position_id, timestamp, action)
)
"""


def init_paper_trade_schema(connection: sqlite3.Connection) -> None:
    connection.execute(_CREATE_POSITIONS)
    connection.execute(_CREATE_EVENTS)
    connection.commit()


def upsert_paper_position(connection: sqlite3.Connection, position: Any) -> None:
    connection.execute(
        """
        INSERT INTO paper_positions (
            position_id, pool_address, entry_time, entry_price, min_price, max_price,
            deposit_sol, fee_sol, claimed_sol, status, out_of_range_since,
            entry_x_amount, entry_y_amount, current_x_amount, current_y_amount,
            entry_x_price_usd, entry_y_price_usd, current_x_price_usd, current_y_price_usd
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(position_id) DO UPDATE SET
            pool_address=excluded.pool_address,
            entry_time=excluded.entry_time,
            entry_price=excluded.entry_price,
            min_price=excluded.min_price,
            max_price=excluded.max_price,
            deposit_sol=excluded.deposit_sol,
            fee_sol=excluded.fee_sol,
            claimed_sol=excluded.claimed_sol,
            status=excluded.status,
            out_of_range_since=excluded.out_of_range_since,
            entry_x_amount=excluded.entry_x_amount,
            entry_y_amount=excluded.entry_y_amount,
            current_x_amount=excluded.current_x_amount,
            current_y_amount=excluded.current_y_amount,
            entry_x_price_usd=excluded.entry_x_price_usd,
            entry_y_price_usd=excluded.entry_y_price_usd,
            current_x_price_usd=excluded.current_x_price_usd,
            current_y_price_usd=excluded.current_y_price_usd
        """,
        (
            position.id,
            position.pool_address,
            position.entry_time,
            position.entry_price,
            position.min_price,
            position.max_price,
            position.deposit_sol,
            position.fee_sol,
            position.claimed_sol,
            position.status,
            position.out_of_range_since,
            position.entry_x_amount,
            position.entry_y_amount,
            position.current_x_amount,
            position.current_y_amount,
            position.entry_x_price_usd,
            position.entry_y_price_usd,
            position.current_x_price_usd,
            position.current_y_price_usd,
        ),
    )


def record_paper_event(connection: sqlite3.Connection, event: dict[str, Any]) -> bool:
    cursor = connection.execute(
        """
        INSERT OR IGNORE INTO paper_position_events (
            timestamp, action, position_id, pool_address, price,
            fee_sol, claimed_sol, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event["timestamp"],
            event["action"],
            event["position_id"],
            event["pool_address"],
            event["price"],
            event["fee_sol"],
            event["claimed_sol"],
            event["status"],
        ),
    )
    connection.commit()
    return cursor.rowcount == 1


def load_paper_positions(connection: sqlite3.Connection) -> list[dict[str, Any]]:
    rows = connection.execute(
        "SELECT * FROM paper_positions ORDER BY entry_time, position_id"
    ).fetchall()
    columns = [column[0] for column in connection.execute("PRAGMA table_info(paper_positions)").fetchall()]
    return [dict(zip(columns, row)) for row in rows]
