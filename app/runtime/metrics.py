from __future__ import annotations
def summarize(closed):
    n=len(closed); wins=sum(x.net_pnl_sol>0 for x in closed); pnl=sum(x.net_pnl_sol for x in closed)
    gross_win=sum(x.net_pnl_sol for x in closed if x.net_pnl_sol>0); gross_loss=-sum(x.net_pnl_sol for x in closed if x.net_pnl_sol<0)
    return {"trades":n,"win_rate":wins/n if n else 0.0,"net_pnl_sol":pnl,
            "profit_factor":gross_win/gross_loss if gross_loss else (float("inf") if gross_win else 0.0)}
