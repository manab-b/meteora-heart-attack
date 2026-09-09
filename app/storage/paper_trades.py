from __future__ import annotations

import sqlite3

from app.paper.engine import PaperEngine


def ensure_paper_trades(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS paper_trades(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          pool_address TEXT NOT NULL,
          strategy_key TEXT NOT NULL,
          entry_at REAL NOT NULL,
          exit_at REAL,
          entry_price REAL NOT NULL,
          exit_price REAL,
          gross_pnl_sol REAL DEFAULT 0,
          fees_sol REAL DEFAULT 0,
          net_pnl_sol REAL DEFAULT 0,
          exit_reason TEXT,
          metadata_json TEXT
        );
        CREATE INDEX IF NOT EXISTS idx_paper_trades_strategy ON paper_trades(strategy_key);

        CREATE TABLE IF NOT EXISTS paper_positions(
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
        );
        CREATE TABLE IF NOT EXISTS paper_position_events(
          id INTEGER PRIMARY KEY AUTOINCREMENT,
          position_id TEXT NOT NULL,
          timestamp REAL NOT NULL,
          action TEXT NOT NULL,
          pool_address TEXT NOT NULL,
          price REAL NOT NULL,
          fee_sol REAL NOT NULL,
          claimed_sol REAL NOT NULL,
          status TEXT NOT NULL,
          UNIQUE(position_id, timestamp, action)
        );
        CREATE INDEX IF NOT EXISTS idx_paper_position_events_position
        ON paper_position_events(position_id, timestamp);
        """
    )
    conn.commit()


def record_trade(conn: sqlite3.Connection, **t) -> None:
    ensure_paper_trades(conn)
    keys = ("pool_address", "strategy_key", "entry_at", "exit_at", "entry_price", "exit_price",
            "gross_pnl_sol", "fees_sol", "net_pnl_sol", "exit_reason", "metadata_json")
    with conn:
        conn.execute(
            "INSERT INTO paper_trades(" + ",".join(keys) + ") VALUES(" + ",".join("?" for _ in keys) + ")",
            [t.get(k) for k in keys],
        )


def persist_engine(conn: sqlite3.Connection, engine: PaperEngine) -> None:
    ensure_paper_trades(conn)
    with conn:
        for position in engine.positions.values():
            conn.execute(
                """INSERT INTO paper_positions
                (position_id,pool_address,entry_time,entry_price,min_price,max_price,deposit_sol,
                 fee_sol,claimed_sol,status,out_of_range_since,entry_x_amount,entry_y_amount,
                 current_x_amount,current_y_amount,entry_x_price_usd,entry_y_price_usd,
                 current_x_price_usd,current_y_price_usd)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(position_id) DO UPDATE SET
                  fee_sol=excluded.fee_sol,claimed_sol=excluded.claimed_sol,status=excluded.status,
                  out_of_range_since=excluded.out_of_range_since,current_x_amount=excluded.current_x_amount,
                  current_y_amount=excluded.current_y_amount,current_x_price_usd=excluded.current_x_price_usd,
                  current_y_price_usd=excluded.current_y_price_usd""",
                (position.id, position.pool_address, position.entry_time, position.entry_price,
                 position.min_price, position.max_price, position.deposit_sol, position.fee_sol,
                 position.claimed_sol, position.status, position.out_of_range_since,
                 position.entry_x_amount, position.entry_y_amount, position.current_x_amount,
                 position.current_y_amount, position.entry_x_price_usd, position.entry_y_price_usd,
                 position.current_x_price_usd, position.current_y_price_usd),
            )
        for event in engine.events:
            conn.execute(
                """INSERT OR IGNORE INTO paper_position_events
                (position_id,timestamp,action,pool_address,price,fee_sol,claimed_sol,status)
                VALUES (?,?,?,?,?,?,?,?)""",
                (event["position_id"], event["timestamp"], event["action"], event["pool_address"],
                 event["price"], event["fee_sol"], event["claimed_sol"], event["status"]),
            )


def load_paper_engine(
    conn: sqlite3.Connection,
    *,
    claim_threshold_sol: float = 0.02,
    out_of_range_seconds: int = 20,
) -> PaperEngine:
    ensure_paper_trades(conn)
    engine = PaperEngine(claim_threshold_sol=claim_threshold_sol, out_of_range_seconds=out_of_range_seconds)
    rows = conn.execute(
        "SELECT position_id,pool_address,entry_time,entry_price,min_price,max_price,deposit_sol,fee_sol,
         claimed_sol,status,out_of_range_since,entry_x_amount,entry_y_amount,current_x_amount,current_y_amount,
         entry_x_price_usd,entry_y_price_usd,current_x_price_usd,current_y_price_usd FROM paper_positions"
    ).fetchall()
    for row in rows:
        p = engine.open(row[0], row[1], row[3], row[4], row[5], row[6], timestamp=row[2],
                        x_amount=row[11], y_amount=row[12], x_price_usd=row[15], y_price_usd=row[16])
        p.fee_sol = row[7]
        p.claimed_sol = row[8]
        p.status = row[9]
        p.out_of_range_since = row[10]
        p.current_x_amount = row[13]
        p.current_y_amount = row[14]
        p.current_x_price_usd = row[17]
        p.current_y_price_usd = row[18]
    engine.events.clear()
    return engine
