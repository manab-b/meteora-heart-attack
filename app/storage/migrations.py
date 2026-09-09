from __future__ import annotations
import sqlite3
SCHEMA_VERSION=1
def migrate(conn:sqlite3.Connection)->None:
    conn.execute("CREATE TABLE IF NOT EXISTS schema_meta(version INTEGER NOT NULL)")
    current=conn.execute("SELECT COALESCE(MAX(version),0) FROM schema_meta").fetchone()[0]
    if current<1:
        from app.storage.raw_observations import ensure_raw_observations
        from app.storage.paper_trades import ensure_paper_trades
        from app.storage.equity import ensure_equity
        from app.research.results import ensure_results
        ensure_raw_observations(conn); ensure_paper_trades(conn); ensure_equity(conn); ensure_results(conn)
        conn.execute("INSERT INTO schema_meta(version) VALUES(?)",(1,)); conn.commit()
