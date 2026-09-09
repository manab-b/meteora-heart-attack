from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from typing import Any


def init_raw_schema(connection: sqlite3.Connection) -> None:
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            source TEXT NOT NULL,
            endpoint TEXT NOT NULL,
            pool_address TEXT,
            observed_at TEXT NOT NULL,
            status TEXT NOT NULL,
            payload_json TEXT,
            error TEXT
        )
        """
    )
    connection.execute(
        "CREATE INDEX IF NOT EXISTS idx_raw_snapshots_pool_time ON raw_snapshots(pool_address, observed_at)"
    )
    connection.commit()


def insert_raw_snapshot(
    connection: sqlite3.Connection,
    *,
    source: str,
    endpoint: str,
    pool_address: str | None,
    payload: Any = None,
    status: str = "OK",
    error: str | None = None,
    observed_at: str | None = None,
) -> None:
    timestamp = observed_at or datetime.now(timezone.utc).isoformat()
    connection.execute(
        """
        INSERT INTO raw_snapshots
            (source, endpoint, pool_address, observed_at, status, payload_json, error)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            source,
            endpoint,
            pool_address,
            timestamp,
            status,
            json.dumps(payload, separators=(",", ":"), ensure_ascii=False) if payload is not None else None,
            error,
        ),
    )
    connection.commit()
