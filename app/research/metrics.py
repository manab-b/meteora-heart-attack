from __future__ import annotations
from math import inf

def summarize(pnls:list[float])->dict[str,float]:
    if not pnls: return {"trades":0.0,"net_pnl":0.0,"win_rate":0.0,"profit_factor":0.0,"max_drawdown":0.0}
    wins=sum(x>0 for x in pnls); gross_profit=sum(x for x in pnls if x>0); gross_loss=-sum(x for x in pnls if x<0)
    eq=peak=0.0; dd=0.0
    for x in pnls:
        eq+=x; peak=max(peak,eq); dd=max(dd,peak-eq)
    return {"trades":float(len(pnls)),"net_pnl":sum(pnls),"win_rate":wins/len(pnls),
            "profit_factor":(gross_profit/gross_loss if gross_loss else inf),"max_drawdown":dd}
