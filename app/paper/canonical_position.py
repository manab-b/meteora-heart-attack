from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class CanonicalPositionState:
    position_address: str
    pool_address: str
    observed_at: float
    active_bin_id: int | None
    lower_bin_id: int | None
    upper_bin_id: int | None
    in_range: bool | None
    range_survival_seconds: float
    drain_score: float | None
    x_amount: float | None
    y_amount: float | None
    x_price_sol: float | None
    y_price_sol: float | None
    x_decimals: int | None
    y_decimals: int | None
    fee_x_delta_raw: int
    fee_y_delta_raw: int
    fee_sol: float | None
    reset_or_claim: bool
    position_value_sol: float | None
    eligible_for_mtm: bool
    ineligible_reasons: tuple[str, ...]


def _timestamp(value: str) -> float:
    return datetime.fromisoformat(value.replace("Z", "+00:00")).timestamp()


def _iso_cutoff(observed_at: float) -> str:
    return datetime.fromtimestamp(observed_at, timezone.utc).isoformat()


def _latest_position(connection: sqlite3.Connection, position_address: str, observed_at: float | None = None):
    if observed_at is None:
        return connection.execute(
            """SELECT position_address, pool_address, lower_bin_id, upper_bin_id,
                      deposited_x, deposited_y, observed_at
               FROM position_snapshots
              WHERE position_address = ?
              ORDER BY observed_at DESC, id DESC LIMIT 1""",
            (position_address,),
        ).fetchone()
    return connection.execute(
        """SELECT position_address, pool_address, lower_bin_id, upper_bin_id,
                  deposited_x, deposited_y, observed_at
           FROM position_snapshots
          WHERE position_address = ? AND observed_at <= ?
          ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (position_address, _iso_cutoff(observed_at)),
    ).fetchone()


def _raw_payload(connection: sqlite3.Connection, position_address: str, observed_at: str):
    rows = connection.execute(
        """SELECT payload_json
           FROM raw_snapshots
          WHERE endpoint = 'position_collector'
            AND status = 'OK'
            AND payload_json IS NOT NULL
            AND observed_at <= ?
          ORDER BY observed_at DESC, id DESC""",
        (observed_at,),
    ).fetchall()
    for (payload_json,) in rows:
        payload = json.loads(payload_json)
        if str(payload.get("position_address", payload.get("address", ""))) == position_address:
            return payload
    return None


def _latest_quote(connection: sqlite3.Connection, pool_address: str, side: str, observed_at: float, max_age: float):
    row = connection.execute(
        """SELECT price_sol, observed_at, source
           FROM token_quotes
          WHERE pool_address = ? AND token_side = ? AND observed_at <= ?
          ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (pool_address, side, observed_at),
    ).fetchone()
    if row is None:
        return None
    age = observed_at - float(row[1])
    if age < 0 or age > max_age:
        return None
    price = float(row[0])
    if price <= 0:
        return None
    return price


def _latest_analytics(connection: sqlite3.Connection, position_address: str, observed_at: float):
    return connection.execute(
        """SELECT active_bin_id, lower_bin_id, upper_bin_id, in_range,
                  range_survival_seconds, fee_x_delta_raw, fee_y_delta_raw,
                  reset_or_claim, fee_sol
           FROM position_analytics
          WHERE position_address = ? AND observed_at <= ?
          ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (position_address, observed_at),
    ).fetchone()


def _drain_score(connection: sqlite3.Connection, pool_address: str, active_bin_id: int | None, observed_at: float):
    if active_bin_id is None:
        return None
    row = connection.execute(
        """SELECT score
           FROM bin_drain_events
          WHERE pool_address = ? AND bin_id = ? AND observed_at <= ?
          ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (pool_address, active_bin_id, observed_at),
    ).fetchone()
    return None if row is None else float(row[0])


def _active_bin_price(connection: sqlite3.Connection, pool_address: str, active_bin_id: int | None, observed_at: float):
    if active_bin_id is None:
        return None
    row = connection.execute(
        """SELECT price
           FROM bin_liquidity_snapshots
          WHERE pool_address = ? AND bin_id = ? AND observed_at <= ?
          ORDER BY observed_at DESC, id DESC LIMIT 1""",
        (pool_address, active_bin_id, observed_at),
    ).fetchone()
    return None if row is None else float(row[0])


def load_canonical_position_state(
    connection: sqlite3.Connection,
    position_address: str,
    *,
    observed_at: float | None = None,
    max_quote_age_seconds: float = 120.0,
) -> CanonicalPositionState | None:
    """Reconstruct one position state strictly from persisted observations.

    ``observed_at`` selects the latest observation at or before that point,
    allowing historical paper replay without looking ahead to later snapshots.
    Missing facts make MTM ineligible rather than being filled with estimates.
    """
    row = _latest_position(connection, position_address, observed_at)
    if row is None:
        return None

    position_address, pool_address, lower_bin_id, upper_bin_id, raw_x, raw_y, observed_at_text = row
    state_observed_at = _timestamp(str(observed_at_text))
    if observed_at is not None and state_observed_at > observed_at:
        return None
    payload = _raw_payload(connection, position_address, str(observed_at_text))
    x_decimals = payload.get("token_x_decimals") if payload else None
    y_decimals = payload.get("token_y_decimals") if payload else None
    x_decimals = int(x_decimals) if x_decimals is not None else None
    y_decimals = int(y_decimals) if y_decimals is not None else None

    analytics = _latest_analytics(connection, position_address, state_observed_at)
    if analytics is None:
        active_bin_id = None
        in_range = None
        survival = 0.0
        fee_x_delta_raw = 0
        fee_y_delta_raw = 0
        reset_or_claim = False
        fee_sol = None
    else:
        active_bin_id = None if analytics[0] is None else int(analytics[0])
        lower_bin_id = analytics[1] if analytics[1] is not None else lower_bin_id
        upper_bin_id = analytics[2] if analytics[2] is not None else upper_bin_id
        in_range = None if analytics[3] is None else bool(analytics[3])
        survival = float(analytics[4])
        fee_x_delta_raw = int(analytics[5])
        fee_y_delta_raw = int(analytics[6])
        reset_or_claim = bool(analytics[7])
        fee_sol = None if analytics[8] is None else float(analytics[8])

    x_price_sol = _latest_quote(connection, pool_address, "x", state_observed_at, max_quote_age_seconds)
    y_price_sol = _latest_quote(connection, pool_address, "y", state_observed_at, max_quote_age_seconds)
    reasons: list[str] = []
    if x_decimals is None:
        reasons.append("missing_x_decimals")
    if y_decimals is None:
        reasons.append("missing_y_decimals")
    if x_price_sol is None:
        reasons.append("missing_or_stale_x_price")
    if y_price_sol is None:
        reasons.append("missing_or_stale_y_price")

    x_amount = int(str(raw_x)) / (10 ** x_decimals) if x_decimals is not None else None
    y_amount = int(str(raw_y)) / (10 ** y_decimals) if y_decimals is not None else None
    position_value_sol = None
    if not reasons:
        position_value_sol = x_amount * x_price_sol + y_amount * y_price_sol

    return CanonicalPositionState(
        position_address=str(position_address),
        pool_address=str(pool_address),
        observed_at=state_observed_at,
        active_bin_id=active_bin_id,
        lower_bin_id=None if lower_bin_id is None else int(lower_bin_id),
        upper_bin_id=None if upper_bin_id is None else int(upper_bin_id),
        in_range=in_range,
        range_survival_seconds=survival,
        drain_score=_drain_score(connection, str(pool_address), active_bin_id, state_observed_at),
        x_amount=x_amount,
        y_amount=y_amount,
        x_price_sol=x_price_sol,
        y_price_sol=y_price_sol,
        x_decimals=x_decimals,
        y_decimals=y_decimals,
        fee_x_delta_raw=fee_x_delta_raw,
        fee_y_delta_raw=fee_y_delta_raw,
        fee_sol=fee_sol,
        reset_or_claim=reset_or_claim,
        position_value_sol=position_value_sol,
        eligible_for_mtm=not reasons,
        ineligible_reasons=tuple(reasons),
    )


def active_bin_price(state: CanonicalPositionState, connection: sqlite3.Connection) -> float | None:
    """Return the persisted active-bin price for diagnostics without estimation."""
    return _active_bin_price(connection, state.pool_address, state.active_bin_id, state.observed_at)
