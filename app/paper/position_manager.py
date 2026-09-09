from __future__ import annotations
from app.paper.paper_position import PaperPosition
from app.paper.trade_math import pnl_sol,net_pnl

class PositionManager:
    def __init__(self): self.positions={}

    def open(self,pool,strategy,at,price,notional_sol):
        key=(pool,strategy)
        if key in self.positions: return None
        p=PaperPosition(pool,strategy,at,price,notional_sol)
        self.positions[key]=p; return p

    def close(self,pool,strategy,at,price,reason,fees_sol=0.0):
        p=self.positions.get((pool,strategy))
        if not p: return None
        p.close(at,price,reason,fees_sol)
        gross=pnl_sol(p.entry_price,price,p.notional_sol)
        result={"position":p,"gross_pnl_sol":gross,"fees_sol":p.fees_sol,"net_pnl_sol":net_pnl(gross,p.fees_sol)}
        self.positions.pop((pool,strategy),None)
        return result
