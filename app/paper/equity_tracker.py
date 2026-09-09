from __future__ import annotations
class EquityTracker:
    def __init__(self,initial_sol:float=5.0):
        if initial_sol<=0: raise ValueError("initial_sol must be positive")
        self.equity_sol=initial_sol; self.fees_sol=0.0; self.peak_sol=initial_sol; self.max_drawdown_sol=0.0
    def apply(self,net_pnl_sol:float,fees_sol:float=0.0):
        self.equity_sol+=net_pnl_sol; self.fees_sol+=fees_sol
        self.peak_sol=max(self.peak_sol,self.equity_sol)
        self.max_drawdown_sol=max(self.max_drawdown_sol,self.peak_sol-self.equity_sol)
        return self.equity_sol
