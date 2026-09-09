import sqlite3

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


def test_replay_uses_position_fee_not_pool_volume():
    conn = _connection()
    for ts, price in ((0.0, 1.0), (60.0, 1.01), (120.0, 1.02)):
        for bin_id, bin_price in ((9, 0.99), (10, price), (11, 1.03)):
            _bin(conn, "P", bin_id, ts, bin_price)
    for ts, fee, active in ((0.0, 0.0, 10), (60.0, 0.01, 10), (120.0, 0.02, 10)):
        insert_position_analytics(
            conn,
            position_address="POS",
            pool_address="P",
            observed_at=ts,
            active_bin_id=active,
            lower_bin_id=9,
            upper_bin_id=11,
            in_range=True,
            range_survival_seconds=ts,
            fee_x_delta_raw=0,
            fee_y_delta_raw=0,
            reset_or_claim=False,
            fee_sol=fee,
            source="test",
        )

    points = build_replay_points(conn, position_address="POS")
    assert [round(point.fee_delta_sol, 4) for point in points] == [0.0, 0.01, 0.02]
    assert points[-1].fee_velocity_sol_min > 0


def test_replay_exits_on_observed_drain_score():
    conn = _connection()
    for ts in (0.0, 60.0):
        _bin(conn, "P", 10, ts, 1.0)
        _bin(conn, "P", 9, ts, 0.99)
        _bin(conn, "P", 11, ts, 1.01)
    insert_position_analytics(
        conn, position_address="POS", pool_address="P", observed_at=0.0,
        active_bin_id=10, lower_bin_id=9, upper_bin_id=11, in_range=True,
        range_survival_seconds=0, fee_x_delta_raw=0, fee_y_delta_raw=0,
        reset_or_claim=False, fee_sol=0.0, source="test",
    )
    insert_position_analytics(
        conn, position_address="POS", pool_address="P", observed_at=60.0,
        active_bin_id=10, lower_bin_id=9, upper_bin_id=11, in_range=True,
        range_survival_seconds=60, fee_x_delta_raw=0, fee_y_delta_raw=0,
        reset_or_claim=False, fee_sol=0.01, source="test",
    )
    conn.execute(
        """INSERT INTO bin_drain_events
        (pool_address,bin_id,previous_observed_at,observed_at,elapsed_seconds,
         active_bin_moved,depletion_ratio,score,source)
        VALUES ('P',10,0,60,60,0,0.99,0.99,'test')"""
    )
    conn.commit()

    result = replay_position(conn, position_address="POS", max_drain_score=0.95)
    assert result.closed
    assert any(event["action"] == "DRAIN_EXIT" for event in result.events)
