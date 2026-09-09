from __future__ import annotations
def snapshot(ledger,checkpoint,last_cycle=None):
    closed=ledger.closed
    return {"open_positions":len(ledger.open),"closed_trades":len(closed),
            "net_pnl_sol":sum(t.net_pnl_sol for t in closed),
            "runtime":{"cycles":checkpoint.cycles,"errors":checkpoint.errors,
                       "healthy":checkpoint.healthy},
            "last_cycle":last_cycle}
