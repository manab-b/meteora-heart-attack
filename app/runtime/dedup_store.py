from __future__ import annotations

import sqlite3


class DedupStore:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        self.conn.execute(
            "CREATE TABLE IF NOT EXISTS runtime_keys(key TEXT PRIMARY KEY, created_at REAL NOT NULL)"
        )
        self.conn.commit()

    def claim(self, key: str, created_at: float) -> bool:
        cur = self.conn.execute(
            "INSERT OR IGNORE INTO runtime_keys(key,created_at) VALUES(?,?)",
            (key, created_at),
        )
        self.conn.commit()
        return cur.rowcount == 1

    def release(self, key: str) -> None:
        """Remove a claimed key when downstream persistence failed.

        A claim is only useful if the observation was actually persisted. This
        makes transient collector/DB failures retryable on the next cycle.
        """
        self.conn.execute("DELETE FROM runtime_keys WHERE key = ?", (key,))
        self.conn.commit()
