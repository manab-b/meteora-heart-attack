import sqlite3

import pytest

from app.research.paper_replay import build_replay_points, replay_position
from app.storage.bin_drain import init_bin_drain_schema
from app.storage.bin_liquidity import init_bin_liquidity_schema
from app.storage.position_analytics import init_position_analytics_schema, insert_position_analytics


def _connection():
    conn = sqlite3.connect(":memory:")
    init_bin_liquidity_schema(conn)
    init_bin_drain_schema(conn)
    init_position_analytics_schema(conn)
    return conn


def _bin(conn, pool, bin_id, ts, price):
    conn.execute(
        """INSERT INTO bin_liquidity_snapshots
        (pool_address,bin_id,active_bin_id,price,x_amount_raw,y_amount_raw,observed_at,source)
        VALUES (?,?,?,?,?,?,?,?)""",
        (pool, bin_id, 10, str(price), "100", "100", ts, "test"),
    )
    conn.commit()


def _drain(conn, ts, score):
    conn.execute(
        """INSERT INTO bin_drain_events
        (pool_address,bin_id,previous_observed_at,observed_at,elapsed_seconds,
         active_bin_moved,depletion_ratio,score,source)
        VALUES ('P',10,?, ?,60,0,?,?, 'test')""",
        (max(0.0, ts - 60.0), ts, score, score),
    )
    conn.commit()


def _analytics(conn, ts, fee, in_range=True):
    insert_position_analytics(
        conn,
        position_address="POS",
        pool_address="P",
        observed_at=ts,
        active_bin_id=10,
        lower_bin_id=9,
        upper_bin_id=11,
        in_range=in_range,
        range_survival_seconds=ts,
        fee_x_delta_raw=0,
        fee_y_delta_raw=0,
        reset_or_claim=False,
        fee_sol=fee,
        source="test",
    )


def test_replay_uses_position_fee_not_pool_volume():
    conn = _connection()
    for ts, price in ((0.0, 1.0), (60.0, 1.01), (120.0, 1.02)):
        for bin_id, bin_price in ((9, 0.99), (10, price), (11, 1.03)):
            _bin(conn, "P", bin_id, ts, bin_price)
        _drain(conn, ts, 0.0)
    for ts, fee in ((0.0, 0.0), (60.0, 0.01), (120.0, 0.02)):
        _analytics(conn, ts, fee)

    points = build_replay_points(conn, position_address="POS")
    assert [round(point.fee_delta_sol, 4) for point in points] == [0.0, 0.01, 0.02]
    assert points[-1].fee_velocity_sol_min > 0


def test_replay_requires_authoritative_drain_observation():
    conn = _connection()
    for ts in (0.0, 60.0):
        for bin_id, price in ((9, 0.99), (10, 1.0), (11, 1.01)):
            _bin(conn, "P", bin_id, ts, price)
        _analytics(conn, ts, 0.01)

    result = replay_position(conn, position_address="POS")
    assert result.points == ()
    assert result.skipped == ("no_valid_authoritative_points",)


def test_replay_enters_only_after_canonical_signal_is_ready():
    conn = _connection()
    for ts in (0.0, 60.0):
        for bin_id, price in ((9, 0.99), (10, 1.0), (11, 1.01)):
            _bin(conn, "P", bin_id, ts, price)
        _drain(conn, ts, 0.0)
    _analytics(conn, 0.0, 0.0)
    _analytics(conn, 60.0, 0.02)

    result = replay_position(conn, position_address="POS", min_fee_velocity_sol_min=0.01)
    assert any(event["action"] == "OPEN" for event in result.events)
    assert result.events[0]["timestamp"] == pytest.approx(60.0)


def test_replay_exits_on_observed_drain_score():
    conn = _connection()
    for ts in (0.0, 60.0):
        _bin(conn, "P", 10, ts, 1.0)
        _bin(conn, "P", 9, ts, 0.99)
        _bin(conn, "P", 11, ts, 1.01)
    _drain(conn, 0.0, 0.0)
    _drain(conn, 60.0, 0.99)
    _analytics(conn, 0.0, 0.0)
    _analytics(conn, 60.0, 0.01)

    result = replay_position(conn, position_address="POS", max_drain_score=0.95)
    assert result.closed
    assert any(event["action"] == "DRAIN_EXIT" for event in result.events)
