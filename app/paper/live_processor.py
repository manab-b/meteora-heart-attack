from __future__ import annotations
from app.paper.position_manager import PositionManager
from app.paper.entry_rules import decide_entry
from app.paper.exit_rules import should_exit
from app.paper.trade_math import pnl_sol,net_pnl
from app.storage.paper_trades import record_trade

class LivePaperProcessor:
    def __init__(self,conn,strategy_key:str,notional_sol:float,min_score:float,max_out_seconds:int,manager=None):
        self.conn=conn; self.strategy_key=strategy_key; self.notional_sol=notional_sol
        self.min_score=min_score; self.max_out_seconds=max_out_seconds
        self.manager=manager or PositionManager()

    def process(self,pool,tick,state,score:float,min_price:float,max_price:float):
        pos=self.manager.positions.get((pool,self.strategy_key))
        if pos is None:
            d=decide_entry(score=score,min_score=self.min_score,already_open=False)
            if d.action=="OPEN":
                return self.manager.open(pool,self.strategy_key,tick.observed_at,tick.price,self.notional_sol)
            return None
        exit_now,reason=should_exit(in_range=min_price<=tick.price<=max_price,
            out_of_range_seconds=state.out_of_range_seconds,max_out_seconds=self.max_out_seconds,
            rug_flags=state.rug_flags)
        if exit_now:
            result=self.manager.close(pool,self.strategy_key,tick.observed_at,tick.price,reason,state.fee_usd)
            if result:
                record_trade(self.conn,pool_address=pool,strategy_key=self.strategy_key,
                  entry_at=result["position"].entry_at,exit_at=result["position"].exit_at,
                  entry_price=result["position"].entry_price,exit_price=result["position"].exit_price,
                  gross_pnl_sol=result["gross_pnl_sol"],fees_sol=result["fees_sol"],
                  net_pnl_sol=result["net_pnl_sol"],exit_reason=reason,metadata_json="{}")
            return result
        return pos
