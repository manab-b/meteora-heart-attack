import sqlite3

from app.paper.engine import PaperEngine
from app.storage.migrations import initialize_database
from app.storage.paper_trades import load_paper_engine, persist_engine


def test_paper_engine_round_trips_through_storage():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    engine = PaperEngine()
    engine.open(
        "paper:POOL:100",
        "POOL",
        price=10.0,
        min_price=9.0,
        max_price=11.0,
        deposit_sol=1.0,
        timestamp=100.0,
    )
    engine.tick("paper:POOL:100", price=10.2, fee_delta_sol=0.01, timestamp=110.0)
    persist_engine(connection, engine)

    restored = load_paper_engine(connection)
    position = restored.positions["paper:POOL:100"]
    assert position.status == "OPEN"
    assert position.fee_sol == 0.01
    assert position.entry_price == 10.0
    assert len(connection.execute("SELECT 1 FROM paper_position_events").fetchall()) == 1


def test_paper_event_persistence_is_idempotent():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    engine = PaperEngine()
    engine.open("paper:POOL:100", "POOL", 10.0, 9.0, 11.0, 1.0, timestamp=100.0)
    persist_engine(connection, engine)
    persist_engine(connection, engine)

    count = connection.execute("SELECT COUNT(*) FROM paper_position_events").fetchone()[0]
    assert count == 1
