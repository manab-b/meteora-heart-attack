import sqlite3

import pytest

from app.research.paper_replay import build_replay_points, replay_position
from app.storage.bin_drain import init_bin_drain_schema
from app.storage.bin_liquidity import init_bin_liquidity_schema
from app.storage.position_analytics import init_position_analytics_schema, insert_position_analytics
from app.storage.raw import init_raw_schema, insert_raw_snapshot
from app.storage.token_quotes import init_token_quote_schema, insert_token_quote


def _connection():
    conn = sqlite3.connect(":memory:")
    init_raw_schema(conn)
    init_token_quote_schema(conn)
    init_bin_liquidity_schema(conn)
    init_bin_drain_schema(conn)
    init_position_analytics_schema(conn)
    conn.execute(
        """CREATE TABLE position_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position_address TEXT NOT NULL,
            owner TEXT,
            pool_address TEXT NOT NULL,
            lower_bin_id INTEGER,
            upper_bin_id INTEGER,
            deposited_x TEXT NOT NULL,
            deposited_y TEXT NOT NULL,
            unclaimed_fee_x TEXT,
            unclaimed_fee_y TEXT,
            observed_at TEXT NOT NULL,
            source TEXT NOT NULL
        )"""
    )
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


def test_replay_does_not_enter_without_canonical_position_state():
    conn = _connection()
    for ts in (0.0, 60.0):
        for bin_id, price in ((9, 0.99), (10, 1.0), (11, 1.01)):
            _bin(conn, "P", bin_id, ts, price)
        _drain(conn, ts, 0.0)
    _analytics(conn, 0.0, 0.0)
    _analytics(conn, 60.0, 0.02)

    result = replay_position(conn, position_address="POS", min_fee_velocity_sol_min=0.01)
    assert not any(event["action"] == "OPEN" for event in result.events)
    assert result.skipped == ("60.0:NO_CANONICAL_STATE",)


def test_replay_exits_on_observed_drain_score():
    conn = _connection()
    for iso_ts, ts, drain_score, fee in (
        ("1970-01-01T00:00:00+00:00", 0.0, 0.0, 0.0),
        ("1970-01-01T00:01:00+00:00", 60.0, 0.99, 0.01),
    ):
        for bin_id, price in ((9, 0.99), (10, 1.0), (11, 1.01)):
            _bin(conn, "P", bin_id, ts, price)
        _drain(conn, ts, drain_score)
        _analytics(conn, ts, fee)
        conn.execute(
            """INSERT INTO position_snapshots
            (position_address,owner,pool_address,lower_bin_id,upper_bin_id,
             deposited_x,deposited_y,unclaimed_fee_x,unclaimed_fee_y,observed_at,source)
            VALUES ('POS','OWNER','P',9,11,'100','100','0','0',?,'test')""",
            (iso_ts,),
        )
        insert_raw_snapshot(
            conn,
            source="test",
            endpoint="position_collector",
            pool_address="P",
            observed_at=iso_ts,
            payload={"position_address": "POS", "token_x_decimals": 0, "token_y_decimals": 0},
        )
        insert_token_quote(conn, pool_address="P", token_side="x", price_sol=1.0, observed_at=ts, source="test")
        insert_token_quote(conn, pool_address="P", token_side="y", price_sol=1.0, observed_at=ts, source="test")
    conn.commit()

    result = replay_position(conn, position_address="POS", max_drain_score=0.95)
    assert result.closed
    assert any(event["action"] == "DRAIN_EXIT" for event in result.events)


def test_replay_calculates_dlmm_pnl_from_historical_canonical_states():
    conn = _connection()
    observations = (
        ("1970-01-01T00:00:00+00:00", 0.0, 0.0, 0.0),
        ("1970-01-01T00:01:00+00:00", 60.0, 0.0, 0.02),
        ("1970-01-01T00:02:00+00:00", 120.0, 0.99, 0.01),
    )
    for iso_ts, ts, drain_score, fee in observations:
        conn.execute(
            """INSERT INTO position_snapshots
            (position_address,owner,pool_address,lower_bin_id,upper_bin_id,
             deposited_x,deposited_y,unclaimed_fee_x,unclaimed_fee_y,observed_at,source)
            VALUES ('POS','OWNER','P',9,11,'100','100','0','0',?,'test')""",
            (iso_ts,),
        )
        insert_raw_snapshot(
            conn,
            source="test",
            endpoint="position_collector",
            pool_address="P",
            observed_at=iso_ts,
            payload={
                "position_address": "POS",
                "token_x_decimals": 0,
                "token_y_decimals": 0,
            },
        )
        insert_token_quote(conn, pool_address="P", token_side="x", price_sol=1.0, observed_at=ts, source="test")
        insert_token_quote(conn, pool_address="P", token_side="y", price_sol=1.0, observed_at=ts, source="test")
        for bin_id, price in ((9, 0.99), (10, 1.0), (11, 1.01)):
            _bin(conn, "P", bin_id, ts, price)
        _drain(conn, ts, drain_score)
        _analytics(conn, ts, fee)
    conn.commit()

    result = replay_position(conn, position_address="POS", min_fee_velocity_sol_min=0.01)

    assert result.closed
    assert result.dlmm_pnl is not None
    assert result.dlmm_pnl.entry_value_sol == pytest.approx(200.0)
    assert result.dlmm_pnl.current_value_sol == pytest.approx(200.0)
    assert result.dlmm_pnl.fees_sol == pytest.approx(0.03)
    assert result.dlmm_pnl.net_pnl_sol == pytest.approx(0.03)


def test_historical_canonical_replay_does_not_look_ahead():
    conn = _connection()
    for iso_ts, ts, raw_x in (
        ("1970-01-01T00:01:00+00:00", 60.0, "100"),
        ("1970-01-01T00:02:00+00:00", 120.0, "200"),
    ):
        conn.execute(
            """INSERT INTO position_snapshots
            (position_address,owner,pool_address,lower_bin_id,upper_bin_id,
             deposited_x,deposited_y,unclaimed_fee_x,unclaimed_fee_y,observed_at,source)
            VALUES ('POS','OWNER','P',9,11,?, '100','0','0',?,'test')""",
            (raw_x, iso_ts),
        )
        insert_raw_snapshot(
            conn,
            source="test",
            endpoint="position_collector",
            pool_address="P",
            observed_at=iso_ts,
            payload={"position_address": "POS", "token_x_decimals": 0, "token_y_decimals": 0},
        )
        insert_token_quote(conn, pool_address="P", token_side="x", price_sol=1.0, observed_at=ts, source="test")
        insert_token_quote(conn, pool_address="P", token_side="y", price_sol=1.0, observed_at=ts, source="test")
        for bin_id, price in ((9, 0.99), (10, 1.0), (11, 1.01)):
            _bin(conn, "P", bin_id, ts, price)
        _drain(conn, ts, 0.0)
        _analytics(conn, ts, 0.0)
    conn.commit()

    from app.paper.canonical_position import load_canonical_position_state

    state = load_canonical_position_state(conn, "POS", observed_at=60.0)
    assert state is not None
    assert state.observed_at == pytest.approx(60.0)
    assert state.x_amount == pytest.approx(100.0)
