from __future__ import annotations
from app.paper.position_manager import PositionManager
from app.paper.entry_rules import decide_entry
from app.paper.exit_rules import should_exit
from app.storage.paper_trades import record_trade

class LivePaperProcessor:
    def __init__(self,conn,strategy_key:str,notional_sol:float,min_score:float,max_out_seconds:int,manager=None):
        self.conn=conn; self.strategy_key=strategy_key; self.notional_sol=notional_sol
        self.min_score=min_score; self.max_out_seconds=max_out_seconds
        self.manager=manager or PositionManager()

    def process(self,pool,tick,state,score:float,range_state):
        pos=self.manager.positions.get((pool,self.strategy_key))
        if pos is None:
            decision=decide_entry(score=score,min_score=self.min_score,already_open=False)
            if decision.action=="OPEN" and range_state is not None and range_state.in_range:
                return self.manager.open(pool,self.strategy_key,tick.observed_at,tick.price,self.notional_sol)
            return None
        if range_state is None:
            return pos
        exit_now,reason=should_exit(
            in_range=range_state.in_range,
            out_of_range_seconds=int(state.out_of_range_seconds),
            max_out_seconds=self.max_out_seconds,
            rug_flags=state.rug_flags,
        )
        if exit_now:
            # Fee is deliberately not converted here: pool fee USD and SOL
            # are different units. Position-level SOL fee accrual must be supplied.
            result=self.manager.close(pool,self.strategy_key,tick.observed_at,tick.price,reason,0.0)
            if result:
                record_trade(self.conn,pool_address=pool,strategy_key=self.strategy_key,
                  entry_at=result["position"].entry_at,exit_at=result["position"].exit_at,
                  entry_price=result["position"].entry_price,exit_price=result["position"].exit_price,
                  gross_pnl_sol=result["gross_pnl_sol"],fees_sol=result["fees_sol"],
                  net_pnl_sol=result["net_pnl_sol"],exit_reason=reason,metadata_json="{}")
            return result
        return pos
