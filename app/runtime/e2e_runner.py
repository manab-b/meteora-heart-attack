from __future__ import annotations

from app.runtime.e2e_cycle import evaluate_observation
from app.runtime.observation_adapter import adapt
from app.runtime.paper_ledger import PaperTrade
from app.runtime.paper_persistence import save_closed, save_open


class E2ERunner:
    def __init__(self, ledger, conn=None, size_sol=1.0):
        self.ledger = ledger
        self.conn = conn
        self.size_sol = size_sol

    def process(self, raw, strategy_key, now):
        obs = adapt(raw, strategy_key)
        decision = evaluate_observation(raw, strategy_key)
        trade_id = f"{obs.pool_address}:{strategy_key}"

        if decision.entry and trade_id not in self.ledger.open:
            trade = PaperTrade(trade_id, strategy_key, obs.pool_address, now, obs.price, self.size_sol)
            if self.ledger.enter(trade):
                if self.conn is not None:
                    save_open(self.conn, trade)
                return "ENTRY"

        if decision.exit and trade_id in self.ledger.open:
            closed = self.ledger.exit(trade_id, now, obs.price, decision.reason)
            if self.conn is not None:
                save_closed(self.conn, closed)
            return "EXIT"

        return "HOLD" if trade_id in self.ledger.open else "WAIT"
