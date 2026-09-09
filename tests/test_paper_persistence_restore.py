import sqlite3

from app.runtime.paper_ledger import PaperTrade
from app.runtime.paper_persistence import init, load_ledger, save_closed, save_open


def test_load_ledger_restores_open_and_closed_trades():
    conn = sqlite3.connect(":memory:")
    init(conn)

    open_trade = PaperTrade("open:strategy", "strategy", "pool-open", 1.0, 100.0, 1.0)
    closed_trade = PaperTrade("closed:strategy", "strategy", "pool-closed", 2.0, 100.0, 1.0)
    save_open(conn, open_trade)
    save_open(conn, closed_trade)

    conn.execute(
        "UPDATE paper_trades SET exit_at=?, exit_price=?, net_pnl_sol=?, exit_reason=? WHERE trade_id=?",
        (3.0, 110.0, 0.1, "target", closed_trade.trade_id),
    )
    conn.commit()

    restored = load_ledger(conn)
    assert set(restored.open) == {open_trade.trade_id}
    assert len(restored.closed) == 1
    assert restored.closed[0].trade.trade_id == closed_trade.trade_id
    assert restored.closed[0].net_pnl_sol == 0.1
