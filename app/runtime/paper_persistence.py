from __future__ import annotations

from app.runtime.paper_ledger import PaperTrade, PaperLedger


def init(conn):
    conn.execute("""CREATE TABLE IF NOT EXISTS paper_trades(
      trade_id TEXT PRIMARY KEY,strategy_key TEXT NOT NULL,pool_address TEXT NOT NULL,
      entry_at REAL NOT NULL,entry_price REAL NOT NULL,size_sol REAL NOT NULL,
      exit_at REAL,exit_price REAL,net_pnl_sol REAL,exit_reason TEXT)""")
    conn.commit()


def save_open(conn, t):
    conn.execute(
        "INSERT OR IGNORE INTO paper_trades(trade_id,strategy_key,pool_address,entry_at,entry_price,size_sol) VALUES(?,?,?,?,?,?)",
        (t.trade_id, t.strategy_key, t.pool_address, t.entry_at, t.entry_price, t.size_sol),
    )
    conn.commit()


def save_closed(conn, c):
    conn.execute(
        "UPDATE paper_trades SET exit_at=?,exit_price=?,net_pnl_sol=?,exit_reason=? WHERE trade_id=?",
        (c.exit_at, c.exit_price, c.net_pnl_sol, c.reason, c.trade.trade_id),
    )
    conn.commit()


def load_ledger(conn) -> PaperLedger:
    ledger = PaperLedger()
    rows = conn.execute(
        "SELECT trade_id,strategy_key,pool_address,entry_at,entry_price,size_sol,exit_at,exit_price,net_pnl_sol,exit_reason "
        "FROM paper_trades ORDER BY entry_at, trade_id"
    ).fetchall()
    for row in rows:
        trade = PaperTrade(
            trade_id=str(row[0]), strategy_key=str(row[1]), pool_address=str(row[2]),
            entry_at=float(row[3]), entry_price=float(row[4]), size_sol=float(row[5]),
        )
        if row[6] is None:
            ledger.open[trade.trade_id] = trade
        else:
            from app.runtime.paper_ledger import ClosedTrade
            ledger.closed.append(
                ClosedTrade(trade, float(row[6]), float(row[7]), float(row[8]), str(row[9] or ""))
            )
    return ledger
