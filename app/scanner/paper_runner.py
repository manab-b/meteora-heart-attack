from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.paper.engine import PaperEngine
from app.scanner.live import scan_paper_opportunities
from app.storage.paper_trades import persist_engine
from app.strategy.entry import EntryConfig, should_enter
from app.strategy.exit import ExitConfig, should_exit


@dataclass(frozen=True)
class PaperDecision:
    pool_address: str
    action: str
    reason: str = ""


def evaluate_paper_entries(
    connection: sqlite3.Connection,
    pool_addresses: list[str],
    *,
    entry_config: EntryConfig = EntryConfig(),
    limit: int = 20,
) -> list[PaperDecision]:
    decisions: list[PaperDecision] = []
    for candidate in scan_paper_opportunities(connection, pool_addresses, limit=limit):
        if should_enter(
            candidate.volume_usd,
            candidate.fee_sol_per_minute,
            candidate.drain_score,
            candidate.range_survival_seconds,
            entry_config,
        ):
            decisions.append(PaperDecision(candidate.pool_address, "ENTER"))
    return decisions


def evaluate_paper_exit(
    *,
    pool_address: str = "",
    in_range: bool,
    out_of_range_seconds: float,
    drain_score: float,
    fee_velocity_sol_min: float,
    exit_config: ExitConfig = ExitConfig(),
) -> PaperDecision | None:
    should, reason = should_exit(
        in_range,
        out_of_range_seconds,
        drain_score,
        fee_velocity_sol_min,
        exit_config,
    )
    if should:
        return PaperDecision(pool_address, "EXIT", reason)
    return None


def apply_entry_decisions(
    engine: PaperEngine,
    decisions: list[PaperDecision],
    *,
    price_by_pool: dict[str, float],
    range_by_pool: dict[str, tuple[float, float]],
    deposit_sol: float = 1.0,
    timestamp: float | None = None,
) -> list[str]:
    opened: list[str] = []
    for decision in decisions:
        if decision.action != "ENTER" or decision.pool_address in engine.positions:
            continue
        if decision.pool_address not in price_by_pool or decision.pool_address not in range_by_pool:
            continue
        lower, upper = range_by_pool[decision.pool_address]
        engine.open(
            position_id=f"paper:{decision.pool_address}:{timestamp or 0}",
            pool_address=decision.pool_address,
            price=price_by_pool[decision.pool_address],
            min_price=lower,
            max_price=upper,
            deposit_sol=deposit_sol,
            timestamp=timestamp,
        )
        opened.append(decision.pool_address)
    return opened


def apply_entry_decisions_persisted(
    connection: sqlite3.Connection,
    engine: PaperEngine,
    decisions: list[PaperDecision],
    *,
    price_by_pool: dict[str, float],
    range_by_pool: dict[str, tuple[float, float]],
    deposit_sol: float = 1.0,
    timestamp: float | None = None,
) -> list[str]:
    opened = apply_entry_decisions(
        engine,
        decisions,
        price_by_pool=price_by_pool,
        range_by_pool=range_by_pool,
        deposit_sol=deposit_sol,
        timestamp=timestamp,
    )
    persist_engine(connection, engine)
    return opened
