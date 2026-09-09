import sqlite3

from app.paper.engine import PaperEngine
from app.scanner.paper_runner import apply_paper_tick
from app.storage.migrations import initialize_database


def test_paper_tick_closes_on_liquidity_drain_and_persists_event():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    engine = PaperEngine()
    engine.open("paper:POOL:100", "POOL", 10.0, 9.0, 11.0, 1.0, timestamp=100.0)

    decision = apply_paper_tick(
        connection,
        engine,
        "paper:POOL:100",
        price=10.1,
        fee_delta_sol=0.002,
        timestamp=110.0,
        in_range=True,
        drain_score=0.9,
        fee_velocity_sol_min=0.01,
    )

    assert decision is not None
    assert decision.reason == "LIQUIDITY_DRAIN"
    assert engine.positions["paper:POOL:100"].status == "CLOSED"
    event = connection.execute(
        "SELECT action, status FROM paper_position_events WHERE position_id = ? ORDER BY id DESC LIMIT 1",
        ("paper:POOL:100",),
    ).fetchone()
    assert event == ("LIQUIDITY_DRAIN", "CLOSED")
