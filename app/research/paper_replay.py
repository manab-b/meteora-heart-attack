from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass

from app.metrics.position_pnl import DlmmPnl, dlmm_pnl_from_canonical_states
from app.paper.canonical_position import CanonicalPositionState, load_canonical_position_state
from app.paper.dlmm_signal import evaluate_canonical_state
from app.paper.engine import PaperEngine
from app.storage.paper_trades import ensure_paper_trades, record_trade


@dataclass(frozen=True)
class ReplayPoint:
    position_address: str
    pool_address: str
    observed_at: float
    price: float
    fee_delta_sol: float
    fee_velocity_sol_min: float
    drain_score: float
    in_range: bool
    lower_price: float
    upper_price: float


@dataclass(frozen=True)
class ReplayResult:
    position_address: str
    pool_address: str
    points: tuple[ReplayPoint, ...]
    events: tuple[dict, ...]
    skipped: tuple[str, ...]
    dlmm_pnl: DlmmPnl | None = None

    @property
    def closed(self) -> bool:
        return any(event["action"] in {"OUT_OF_RANGE", "DRAIN_EXIT"} for event in self.events)


def _price_at_bin(
    connection: sqlite3.Connection,
    pool_address: str,
    bin_id: int,
    observed_at: float,
) -> float | None:
    row = connection.execute(
        """SELECT price FROM bin_liquidity_snapshots
        WHERE pool_address = ? AND bin_id = ? AND observed_at <= ?
        ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (pool_address, bin_id, observed_at),
    ).fetchone()
    if row is None or row[0] is None:
        return None
    try:
        price = float(row[0])
    except (TypeError, ValueError):
        return None
    return price if price > 0 else None


def _drain_score(
    connection: sqlite3.Connection,
    pool_address: str,
    bin_id: int,
    observed_at: float,
) -> float | None:
    row = connection.execute(
        """SELECT score FROM bin_drain_events
        WHERE pool_address = ? AND bin_id = ? AND observed_at <= ?
        ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (pool_address, bin_id, observed_at),
    ).fetchone()
    if row is None or row[0] is None:
        return None
    score = float(row[0])
    if not 0.0 <= score <= 1.0:
        raise ValueError("stored drain score must be between 0 and 1")
    return score


def build_replay_points(
    connection: sqlite3.Connection,
    *,
    position_address: str,
    min_fee_velocity_sol_min: float = 0.0,
) -> tuple[ReplayPoint, ...]:
    """Build replay points exclusively from stored position/bin observations.

    Position fees come from ``position_analytics.fee_sol``. Missing fee
    valuation, range facts or drain observations are skipped rather than
    estimated. Pool-wide volume is never used to manufacture position fees.
    """
    if min_fee_velocity_sol_min < 0:
        raise ValueError("min_fee_velocity_sol_min must be non-negative")

    rows = connection.execute(
        """SELECT pool_address, observed_at, active_bin_id, lower_bin_id,
                  upper_bin_id, in_range, fee_sol
        FROM position_analytics
        WHERE position_address = ?
        ORDER BY observed_at ASC, id ASC""",
        (position_address,),
    ).fetchall()
    points: list[ReplayPoint] = []
    previous_at: float | None = None
    for row in rows:
        pool, observed_at, active_bin, lower_bin, upper_bin, in_range, fee_sol = row
        if active_bin is None or lower_bin is None or upper_bin is None or in_range is None:
            continue
        if fee_sol is None:
            continue
        drain_score = _drain_score(connection, pool, int(active_bin), float(observed_at))
        if drain_score is None:
            continue
        price = _price_at_bin(connection, pool, int(active_bin), float(observed_at))
        lower_price = _price_at_bin(connection, pool, int(lower_bin), float(observed_at))
        upper_price = _price_at_bin(connection, pool, int(upper_bin), float(observed_at))
        if price is None or lower_price is None or upper_price is None:
            continue

        observed_at = float(observed_at)
        fee_delta = float(fee_sol)
        if fee_delta < 0:
            raise ValueError("stored fee delta must be non-negative")
        elapsed_min = 0.0 if previous_at is None else (observed_at - previous_at) / 60.0
        if elapsed_min < 0:
            raise ValueError("position observations must be chronological")
        velocity = 0.0 if elapsed_min <= 0 else fee_delta / elapsed_min
        if velocity < min_fee_velocity_sol_min:
            previous_at = observed_at
            continue

        points.append(
            ReplayPoint(
                position_address=position_address,
                pool_address=pool,
                observed_at=observed_at,
                price=price,
                fee_delta_sol=fee_delta,
                fee_velocity_sol_min=velocity,
                drain_score=drain_score,
                in_range=bool(in_range),
                lower_price=min(lower_price, upper_price),
                upper_price=max(lower_price, upper_price),
            )
        )
        previous_at = observed_at
    return tuple(points)


def _historical_canonical_state(
    connection: sqlite3.Connection,
    position_address: str,
    observed_at: float,
) -> CanonicalPositionState | None:
    return load_canonical_position_state(
        connection,
        position_address,
        observed_at=observed_at,
    )


def _authoritative_fee_total(
    connection: sqlite3.Connection,
    position_address: str,
    entry_at: float,
    exit_at: float,
) -> float | None:
    rows = connection.execute(
        """SELECT fee_sol, reset_or_claim
           FROM position_analytics
          WHERE position_address = ?
            AND observed_at >= ?
            AND observed_at <= ?
          ORDER BY observed_at ASC, id ASC""",
        (position_address, entry_at, exit_at),
    ).fetchall()
    if not rows or any(reset_or_claim or fee_sol is None for fee_sol, reset_or_claim in rows):
        return None
    total = sum(float(fee_sol) for fee_sol, _ in rows)
    if total < 0:
        raise ValueError("authoritative fee total must be non-negative")
    return total


def replay_position(
    connection: sqlite3.Connection,
    *,
    position_address: str,
    deposit_sol: float = 1.0,
    out_of_range_seconds: int = 20,
    max_drain_score: float = 0.95,
    min_fee_velocity_sol_min: float = 0.0,
    min_score: float = 0.7,
) -> ReplayResult:
    points = build_replay_points(
        connection,
        position_address=position_address,
        min_fee_velocity_sol_min=min_fee_velocity_sol_min,
    )
    if not points:
        return ReplayResult(position_address, "", (), (), ("no_valid_authoritative_points",))
    if deposit_sol <= 0:
        raise ValueError("deposit_sol must be positive")
    if out_of_range_seconds < 0:
        raise ValueError("out_of_range_seconds must be non-negative")

    engine = PaperEngine(out_of_range_seconds=out_of_range_seconds)
    opened = False
    entry_at: float | None = None
    entry_state: CanonicalPositionState | None = None
    exit_at: float | None = None
    skipped: list[str] = []

    for point in points:
        actual_state = _historical_canonical_state(connection, position_address, point.observed_at)
        if actual_state is None:
            skipped.append(f"{point.observed_at}:NO_CANONICAL_STATE")
            continue
        signal = evaluate_canonical_state(
            actual_state,
            point.fee_velocity_sol_min,
            min_fee_velocity=min_fee_velocity_sol_min,
            max_drain=max_drain_score,
            min_score=min_score,
        )

        if not opened:
            if signal.entry:
                engine.open(
                    position_id=position_address,
                    pool_address=point.pool_address,
                    price=point.price,
                    min_price=point.lower_price,
                    max_price=point.upper_price,
                    deposit_sol=deposit_sol,
                    timestamp=point.observed_at,
                    x_amount=actual_state.x_amount,
                    y_amount=actual_state.y_amount,
                    x_price_usd=None,
                    y_price_usd=None,
                )
                opened = True
                entry_at = point.observed_at
                entry_state = actual_state
            else:
                skipped.append(f"{point.observed_at}:NO_ENTRY")
                continue

        position = engine.positions[position_address]
        if position.status != "OPEN":
            break

        if not point.in_range:
            if position.out_of_range_since is None:
                position.out_of_range_since = point.observed_at
            elif point.observed_at - position.out_of_range_since >= out_of_range_seconds:
                engine.close(position_address, point.price, "OUT_OF_RANGE", point.observed_at)
                exit_at = point.observed_at
                break
        else:
            position.out_of_range_since = None

        if point.drain_score >= max_drain_score:
            engine.close(position_address, point.price, "DRAIN_EXIT", point.observed_at)
            exit_at = point.observed_at
            break

        if point.observed_at != entry_at:
            engine.tick(position_address, point.price, point.fee_delta_sol, point.observed_at)

    pnl: DlmmPnl | None = None
    if entry_at is not None and exit_at is not None and entry_state is not None:
        current_state = _historical_canonical_state(connection, position_address, exit_at)
        fees_sol = _authoritative_fee_total(connection, position_address, entry_at, exit_at)
        if current_state is not None and fees_sol is not None:
            try:
                pnl = dlmm_pnl_from_canonical_states(entry_state, current_state, fees_sol=fees_sol)
            except ValueError:
                pnl = None

    return ReplayResult(
        position_address=position_address,
        pool_address=points[0].pool_address,
        points=points,
        events=tuple(engine.events),
        skipped=tuple(skipped),
        dlmm_pnl=pnl,
    )


def replay_all_positions(
    connection: sqlite3.Connection,
    *,
    deposit_sol: float = 1.0,
    out_of_range_seconds: int = 20,
    max_drain_score: float = 0.95,
    min_fee_velocity_sol_min: float = 0.0,
    min_score: float = 0.7,
) -> tuple[ReplayResult, ...]:
    rows = connection.execute(
        "SELECT DISTINCT position_address FROM position_analytics ORDER BY position_address"
    ).fetchall()
    return tuple(
        replay_position(
            connection,
            position_address=row[0],
            deposit_sol=deposit_sol,
            out_of_range_seconds=out_of_range_seconds,
            max_drain_score=max_drain_score,
            min_fee_velocity_sol_min=min_fee_velocity_sol_min,
            min_score=min_score,
        )
        for row in rows
    )


def persist_replay_result(
    connection: sqlite3.Connection,
    result: ReplayResult,
    *,
    strategy_key: str = "canonical-heart-attack-replay",
) -> bool:
    """Persist one closed replay as a paper trade only when authoritative PnL exists.

    No synthetic PnL, fees, prices, or exit records are created. The deterministic
    position/entry/exit timestamps make repeated replay runs idempotent.
    """
    if not result.closed or result.dlmm_pnl is None or not result.points:
        return False
    open_events = [event for event in result.events if event["action"] == "OPEN"]
    exit_events = [
        event for event in result.events
        if event["action"] in {"OUT_OF_RANGE", "DRAIN_EXIT"}
    ]
    if not open_events or not exit_events:
        return False
    opened = open_events[0]
    exited = exit_events[-1]
    entry_at = float(opened["timestamp"])
    exit_at = float(exited["timestamp"])
    metadata = json.dumps(
        {"position_address": result.position_address, "source": "authoritative_sqlite_replay"},
        sort_keys=True,
    )
    ensure_paper_trades(connection)
    exists = connection.execute(
        """SELECT 1 FROM paper_trades
           WHERE strategy_key = ? AND pool_address = ? AND entry_at = ? AND exit_at = ?
           LIMIT 1""",
        (strategy_key, result.pool_address, entry_at, exit_at),
    ).fetchone()
    if exists is not None:
        return False
    record_trade(
        connection,
        pool_address=result.pool_address,
        strategy_key=strategy_key,
        entry_at=entry_at,
        exit_at=exit_at,
        entry_price=float(opened["price"]),
        exit_price=float(exited["price"]),
        gross_pnl_sol=result.dlmm_pnl.gross_pnl_sol,
        fees_sol=result.dlmm_pnl.fees_sol,
        net_pnl_sol=result.dlmm_pnl.net_pnl_sol,
        exit_reason=exited["action"],
        metadata_json=metadata,
    )
    return True


def persist_replay_results(
    connection: sqlite3.Connection,
    results: tuple[ReplayResult, ...],
    *,
    strategy_key: str = "canonical-heart-attack-replay",
) -> int:
    return sum(persist_replay_result(connection, result, strategy_key=strategy_key) for result in results)
