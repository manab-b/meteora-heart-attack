from __future__ import annotations

import sqlite3


SCHEMA = """
CREATE TABLE IF NOT EXISTS position_analytics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    position_address TEXT NOT NULL,
    pool_address TEXT NOT NULL,
    observed_at REAL NOT NULL,
    active_bin_id INTEGER,
    lower_bin_id INTEGER,
    upper_bin_id INTEGER,
    in_range INTEGER,
    range_survival_seconds REAL NOT NULL,
    fee_x_delta_raw TEXT NOT NULL,
    fee_y_delta_raw TEXT NOT NULL,
    reset_or_claim INTEGER NOT NULL,
    fee_sol REAL,
    source TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_position_analytics_time
ON position_analytics(position_address, observed_at);
"""


def init_position_analytics_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA)
    connection.commit()


def insert_position_analytics(
    connection: sqlite3.Connection,
    *,
    position_address: str,
    pool_address: str,
    observed_at: float,
    active_bin_id: int | None,
    lower_bin_id: int | None,
    upper_bin_id: int | None,
    in_range: bool | None,
    range_survival_seconds: float,
    fee_x_delta_raw: int,
    fee_y_delta_raw: int,
    reset_or_claim: bool,
    fee_sol: float | None,
    source: str,
) -> None:
    if range_survival_seconds < 0:
        raise ValueError("range_survival_seconds must be non-negative")
    if fee_x_delta_raw < 0 or fee_y_delta_raw < 0:
        raise ValueError("fee deltas must be non-negative")
    connection.execute(
        """INSERT INTO position_analytics
        (position_address,pool_address,observed_at,active_bin_id,lower_bin_id,
         upper_bin_id,in_range,range_survival_seconds,fee_x_delta_raw,
         fee_y_delta_raw,reset_or_claim,fee_sol,source)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            position_address,
            pool_address,
            observed_at,
            active_bin_id,
            lower_bin_id,
            upper_bin_id,
            None if in_range is None else int(in_range),
            range_survival_seconds,
            str(fee_x_delta_raw),
            str(fee_y_delta_raw),
            int(reset_or_claim),
            fee_sol,
            source,
        ),
    )
    connection.commit()
