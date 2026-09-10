from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.data_quality.observations import ObservationQualityConfig, assess_observation_quality
from app.paper.canonical_position import CanonicalPositionState
from app.paper.dlmm_signal import evaluate_canonical_state
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
    quality_config: ObservationQualityConfig = ObservationQualityConfig(min_observations=1),
    limit: int = 20,
) -> list[PaperDecision]:
    """Evaluate paper entries; long-history qualification remains a research gate."""
    decisions: list[PaperDecision] = []
    for candidate in scan_paper_opportunities(connection, pool_addresses, limit=limit):
        quality = assess_observation_quality(connection, candidate.pool_address, config=quality_config)
        if not quality.ok:
            continue
        if should_enter(
            candidate.volume_usd,
            candidate.fee_sol_per_minute,
            candidate.drain_score,
            candidate.range_survival_seconds,
            entry_config,
        ):
            decisions.append(PaperDecision(candidate.pool_address, "ENTER"))
    return decisions


def evaluate_canonical_paper_decision(
    state: CanonicalPositionState,
    *,
    fee_velocity_sol_min: float,
    min_fee_velocity: float = 0.0,
    max_drain: float = 0.95,
) -> PaperDecision:
    """Turn one canonical observation into a deterministic paper decision."""
    signal = evaluate_canonical_state(
        state,
        fee_velocity_sol_min,
        min_fee_velocity=min_fee_velocity,
        max_drain=max_drain,
    )
    if signal.entry:
        return PaperDecision(state.pool_address, "ENTER", ",".join(signal.reasons))
    if signal.exit:
        return PaperDecision(state.pool_address, "EXIT", ",".join(signal.reasons))
    return PaperDecision(state.pool_address, "HOLD", ",".join(signal.reasons))


def evaluate_paper_exit(*, pool_address: str = "", in_range: bool, out_of_range_seconds: float,
                        drain_score: float, fee_velocity_sol_min: float,
                        exit_config: ExitConfig = ExitConfig()) -> PaperDecision | None:
    should, reason = should_exit(in_range, out_of_range_seconds, drain_score, fee_velocity_sol_min, exit_config)
    return PaperDecision(pool_address, "EXIT", reason) if should else None


def apply_entry_decisions(engine: PaperEngine, decisions: list[PaperDecision], *,
                          price_by_pool: dict[str, float], range_by_pool: dict[str, tuple[float, float]],
                          deposit_sol: float = 1.0, timestamp: float | None = None) -> list[str]:
    opened: list[str] = []
    for decision in decisions:
        if decision.action != "ENTER" or any(
            p.pool_address == decision.pool_address and p.status == "OPEN" for p in engine.positions.values()
        ):
            continue
        if decision.pool_address not in price_by_pool or decision.pool_address not in range_by_pool:
            continue
        lower, upper = range_by_pool[decision.pool_address]
        engine.open(f"paper:{decision.pool_address}:{timestamp or 0}", decision.pool_address,
                    price_by_pool[decision.pool_address], lower, upper, deposit_sol, timestamp=timestamp)
        opened.append(decision.pool_address)
    return opened


def apply_entry_decisions_persisted(connection: sqlite3.Connection, engine: PaperEngine,
                                    decisions: list[PaperDecision], *,
                                    price_by_pool: dict[str, float], range_by_pool: dict[str, tuple[float, float]],
                                    deposit_sol: float = 1.0, timestamp: float | None = None) -> list[str]:
    opened = apply_entry_decisions(engine, decisions, price_by_pool=price_by_pool,
                                    range_by_pool=range_by_pool, deposit_sol=deposit_sol, timestamp=timestamp)
    persist_engine(connection, engine)
    return opened


def apply_paper_tick(connection: sqlite3.Connection, engine: PaperEngine, position_id: str, *,
                     price: float, fee_delta_sol: float, timestamp: float | None = None,
                     in_range: bool | None = None, drain_score: float = 0.0,
                     fee_velocity_sol_min: float = 0.0, exit_config: ExitConfig = ExitConfig(),
                     x_amount: float | None = None, y_amount: float | None = None,
                     x_price_usd: float | None = None, y_price_usd: float | None = None) -> PaperDecision | None:
    position = engine.positions[position_id]
    if position.status != "OPEN":
        return None
    engine.tick(position_id, price, fee_delta_sol, timestamp,
                x_amount=x_amount, y_amount=y_amount,
                x_price_usd=x_price_usd, y_price_usd=y_price_usd)
    if in_range is None:
        in_range = position.min_price <= price <= position.max_price
    out_of_range_seconds = 0.0
    if not in_range and position.out_of_range_since is not None and timestamp is not None:
        out_of_range_seconds = max(0.0, timestamp - position.out_of_range_since)
    decision = evaluate_paper_exit(pool_address=position.pool_address, in_range=in_range,
                                   out_of_range_seconds=out_of_range_seconds,
                                   drain_score=drain_score, fee_velocity_sol_min=fee_velocity_sol_min,
                                   exit_config=exit_config)
    if decision is not None and position.status == "OPEN":
        engine.close(position_id, price, decision.reason, timestamp)
    persist_engine(connection, engine)
    return decision
