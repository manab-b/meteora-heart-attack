import sqlite3

from app.paper.cycle import PaperMarketTick, run_paper_cycle
from app.paper.engine import PaperEngine
from app.scanner.paper_runner import apply_entry_decisions_persisted
from app.storage.migrations import initialize_database
from app.storage.observations import insert_observation


def test_cycle_does_not_charge_fee_to_new_entry():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    insert_observation(
        connection,
        "POOL",
        1,
        100.0,
        10.0,
        200_000.0,
        0.02,
        0.1,
        120.0,
        True,
    )

    result = run_paper_cycle(
        connection,
        ["POOL"],
        price_by_pool={"POOL": 10.0},
        range_by_pool={"POOL": (9.0, 11.0)},
        market_by_pool={
            "POOL": PaperMarketTick(
                price=10.0,
                fee_delta_sol=0.5,
                fee_velocity_sol_min=0.02,
                drain_score=0.1,
                in_range=True,
            )
        },
        timestamp=100.0,
    )

    assert result.opened_pool_addresses == ("POOL",)
    position = result.engine.positions["paper:POOL:100.0"]
    assert position.fee_sol == 0.0


def test_cycle_ticks_existing_position_and_exits_on_drain():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    engine = PaperEngine()
    apply_entry_decisions_persisted(
        connection,
        engine,
        [],
        price_by_pool={},
        range_by_pool={},
        timestamp=100.0,
    )
    engine.open("paper:POOL:100", "POOL", 10.0, 9.0, 11.0, 1.0, timestamp=100.0)
    from app.storage.paper_trades import persist_engine
    persist_engine(connection, engine)

    result = run_paper_cycle(
        connection,
        [],
        price_by_pool={},
        range_by_pool={},
        market_by_pool={
            "POOL": PaperMarketTick(
                price=10.2,
                fee_delta_sol=0.01,
                fee_velocity_sol_min=0.02,
                drain_score=0.9,
                in_range=True,
            )
        },
        timestamp=110.0,
    )

    assert result.exits[0].reason == "LIQUIDITY_DRAIN"
    assert result.engine.positions["paper:POOL:100"].status == "CLOSED"
