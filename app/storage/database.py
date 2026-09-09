from __future__ import annotations
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS pools (
    address TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    tvl_usd REAL NOT NULL,
    volume_24h_usd REAL NOT NULL,
    fee_24h_usd REAL NOT NULL,
    fee_tvl_ratio_24h REAL NOT NULL,
    current_price REAL NOT NULL,
    dynamic_fee_pct REAL NOT NULL,
    bin_step INTEGER NOT NULL,
    blacklisted INTEGER NOT NULL,
    token_x_symbol TEXT NOT NULL,
    token_y_symbol TEXT NOT NULL,
    fetched_at TEXT NOT NULL
);
"""

class Database:
    def __init__(self, path: str = "data/heart_attack.sqlite3"):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.connection = sqlite3.connect(self.path)
        self.connection.row_factory = sqlite3.Row
        self.connection.execute(SCHEMA)
        self.connection.commit()

    def upsert_pool(self, pool, fetched_at: str) -> None:
        self.connection.execute(
            """
            INSERT INTO pools (
                address, name, tvl_usd, volume_24h_usd, fee_24h_usd,
                fee_tvl_ratio_24h, current_price, dynamic_fee_pct, bin_step,
                blacklisted, token_x_symbol, token_y_symbol, fetched_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(address) DO UPDATE SET
                name=excluded.name, tvl_usd=excluded.tvl_usd,
                volume_24h_usd=excluded.volume_24h_usd, fee_24h_usd=excluded.fee_24h_usd,
                fee_tvl_ratio_24h=excluded.fee_tvl_ratio_24h,
                current_price=excluded.current_price, dynamic_fee_pct=excluded.dynamic_fee_pct,
                bin_step=excluded.bin_step, blacklisted=excluded.blacklisted,
                token_x_symbol=excluded.token_x_symbol, token_y_symbol=excluded.token_y_symbol,
                fetched_at=excluded.fetched_at
            """,
            (pool.address, pool.name, pool.tvl_usd, pool.volume_24h_usd, pool.fee_24h_usd,
             pool.fee_tvl_ratio_24h, pool.current_price, pool.dynamic_fee_pct, pool.bin_step,
             int(pool.blacklisted), pool.token_x_symbol, pool.token_y_symbol, fetched_at),
        )
        self.connection.commit()

    def close(self):
        self.connection.close()
