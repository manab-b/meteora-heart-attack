from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from app.paper.engine import PaperEngine


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
) -> float:
    row = connection.execute(
        """SELECT score FROM bin_drain_events
        WHERE pool_address = ? AND bin_id = ? AND observed_at <= ?
        ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (pool_address, bin_id, observed_at),
    ).fetchone()
    return 0.0 if row is None else max(0.0, min(1.0, float(row[0])))


def build_replay_points(
    connection: sqlite3.Connection,
    *,
    position_address: str,
    min_fee_velocity_sol_min: float = 0.0,
) -> tuple[ReplayPoint, ...]:
    """Build paper-replay points exclusively from stored observations.

    Fee values come from position_analytics.fee_sol. Missing fee valuation is
    intentionally rejected instead of being estimated from pool volume.
    """
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
        if active_bin is None or lower_bin is None or upper_bin is None:
            continue
        if fee_sol is None:
            continue
        price = _price_at_bin(connection, pool, int(active_bin), float(observed_at))
        lower_price = _price_at_bin(connection, pool, int(lower_bin), float(observed_at))
        upper_price = _price_at_bin(connection, pool, int(upper_bin), float(observed_at))
        if price is None or lower_price is None or upper_price is None:
            continue
        elapsed_min = 0.0 if previous_at is None else max(0.0, (float(observed_at) - previous_at) / 60.0)
        velocity = 0.0 if elapsed_min <= 0 else float(fee_sol) / elapsed_min
        if velocity < min_fee_velocity_sol_min:
            continue
        points.append(
            ReplayPoint(
                position_address=position_address,
                pool_address=pool,
                observed_at=float(observed_at),
                price=price,
                fee_delta_sol=max(0.0, float(fee_sol)),
                fee_velocity_sol_min=velocity,
                drain_score=_drain_score(connection, pool, int(active_bin), float(observed_at)),
                in_range=bool(in_range),
                lower_price=min(lower_price, upper_price),
                upper_price=max(lower_price, upper_price),
            )
        )
        previous_at = float(observed_at)
    return tuple(points)


def replay_position(
    connection: sqlite3.Connection,
    *,
    position_address: str,
    deposit_sol: float = 1.0,
    out_of_range_seconds: int = 20,
    max_drain_score: float = 0.95,
    min_fee_velocity_sol_min: float = 0.0,
) -> ReplayResult:
    points = build_replay_points(
        connection,
        position_address=position_address,
        min_fee_velocity_sol_min=min_fee_velocity_sol_min,
    )
    if not points:
        return ReplayResult(position_address, "", (), (), ("no_valid_fee_valued_points",))

    engine = PaperEngine(out_of_range_seconds=out_of_range_seconds)
    first = points[0]
    engine.open(
        position_id=position_address,
        pool_address=first.pool_address,
        price=first.price,
        min_price=first.lower_price,
        max_price=first.upper_price,
        deposit_sol=deposit_sol,
        timestamp=first.observed_at,
    )

    for point in points[1:]:
        if point.drain_score > max_drain_score:
            engine.close(position_address, point.price, "DRAIN_EXIT", point.observed_at)
            break
        engine.tick(
            position_address,
            point.price,
            point.fee_delta_sol,
            point.observed_at,
        )
        if engine.positions[position_address].status != "OPEN":
            break

    skipped = () if len(points) == len(set(p.observed_at for p in points)) else ("duplicate_timestamps",)
    return ReplayResult(
        position_address=position_address,
        pool_address=first.pool_address,
        points=points,
        events=tuple(engine.events),
        skipped=skipped,
    )


def replay_all_positions(
    connection: sqlite3.Connection,
    *,
    deposit_sol: float = 1.0,
    out_of_range_seconds: int = 20,
    max_drain_score: float = 0.95,
    min_fee_velocity_sol_min: float = 0.0,
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
        )
        for row in rows
    )
