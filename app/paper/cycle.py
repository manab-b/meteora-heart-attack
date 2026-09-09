from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.paper.engine import PaperEngine
from app.scanner.paper_runner import (
    PaperDecision,
    apply_entry_decisions_persisted,
    apply_paper_tick,
    evaluate_paper_entries,
)
from app.storage.paper_trades import load_paper_engine
from app.strategy.entry import EntryConfig
from app.strategy.exit import ExitConfig


@dataclass(frozen=True)
class PaperMarketTick:
    price: float
    fee_delta_sol: float
    fee_velocity_sol_min: float
    drain_score: float
    in_range: bool | None = None
    x_amount: float | None = None
    y_amount: float | None = None
    x_price_usd: float | None = None
    y_price_usd: float | None = None


@dataclass(frozen=True)
class PaperCycleResult:
    engine: PaperEngine
    entries: tuple[PaperDecision, ...]
    exits: tuple[PaperDecision, ...]
    opened_pool_addresses: tuple[str, ...]


def run_paper_cycle(
    connection: sqlite3.Connection,
    pool_addresses: list[str],
    *,
    price_by_pool: dict[str, float],
    range_by_pool: dict[str, tuple[float, float]],
    market_by_pool: dict[str, PaperMarketTick],
    timestamp: float,
    deposit_sol: float = 1.0,
    entry_config: EntryConfig = EntryConfig(),
    exit_config: ExitConfig = ExitConfig(),
    limit: int = 20,
) -> PaperCycleResult:
    """Run one complete paper-only observation cycle.

    Fee deltas must come from an authoritative position-level observation. This
    function deliberately does not estimate position fees from pool volume.
    Newly opened positions are not ticked in the same cycle, preventing the
    entry observation from being counted as post-entry performance.
    """
    engine = load_paper_engine(
        connection,
        out_of_range_seconds=exit_config.out_of_range_seconds,
    )
    entries = evaluate_paper_entries(
        connection,
        pool_addresses,
        entry_config=entry_config,
        limit=limit,
    )
    opened = apply_entry_decisions_persisted(
        connection,
        engine,
        entries,
        price_by_pool=price_by_pool,
        range_by_pool=range_by_pool,
        deposit_sol=deposit_sol,
        timestamp=timestamp,
    )

    opened_set = set(opened)
    exits: list[PaperDecision] = []
    for position_id, position in list(engine.positions.items()):
        if position.status != "OPEN" or position.pool_address in opened_set:
            continue
        market = market_by_pool.get(position.pool_address)
        if market is None:
            continue
        decision = apply_paper_tick(
            connection,
            engine,
            position_id,
            price=market.price,
            fee_delta_sol=market.fee_delta_sol,
            timestamp=timestamp,
            in_range=market.in_range,
            drain_score=market.drain_score,
            fee_velocity_sol_min=market.fee_velocity_sol_min,
            exit_config=exit_config,
            x_amount=market.x_amount,
            y_amount=market.y_amount,
            x_price_usd=market.x_price_usd,
            y_price_usd=market.y_price_usd,
        )
        if decision is not None:
            exits.append(decision)

    return PaperCycleResult(
        engine=engine,
        entries=tuple(entries),
        exits=tuple(exits),
        opened_pool_addresses=tuple(opened),
    )
