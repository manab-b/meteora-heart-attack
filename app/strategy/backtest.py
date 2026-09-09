from __future__ import annotations
from dataclasses import dataclass
from .entry import EntryConfig, should_enter
from .exit import ExitConfig, should_exit

@dataclass(frozen=True)
class Observation:
    timestamp: float
    price: float
    volume_usd: float
    fee_velocity_sol_min: float
    drain_score: float
    range_survival_seconds: float
    in_range: bool

@dataclass(frozen=True)
class Trade:
    entry_timestamp: float
    exit_timestamp: float
    entry_price: float
    exit_price: float
    fee_sol: float
    exit_reason: str

class StrategyBacktest:
    def __init__(self, entry: EntryConfig | None = None, exit: ExitConfig | None = None):
        self.entry_cfg = entry or EntryConfig()
        self.exit_cfg = exit or ExitConfig()

    def run(self, observations: list[Observation], fee_per_minute_to_sol: float = 0.0) -> list[Trade]:
        trades: list[Trade] = []
        open_trade = None
        fee_sol = 0.0
        for o in observations:
            if open_trade is None:
                if should_enter(o.volume_usd, o.fee_velocity_sol_min, o.drain_score,
                                o.range_survival_seconds, self.entry_cfg):
                    open_trade = o
                    fee_sol = 0.0
                continue
            elapsed = max(0.0, o.timestamp - open_trade.timestamp)
            fee_sol += max(0.0, fee_per_minute_to_sol) * elapsed / 60.0
            close, reason = should_exit(o.in_range, 0 if o.in_range else elapsed,
                                        o.drain_score, o.fee_velocity_sol_min, self.exit_cfg)
            if close:
                trades.append(Trade(open_trade.timestamp, o.timestamp,
                                    open_trade.price, o.price, fee_sol, reason))
                open_trade = None
        return trades
