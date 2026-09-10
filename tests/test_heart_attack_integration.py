import sqlite3

from app.paper.canonical_position import CanonicalPositionState
from app.paper.cycle import PaperMarketTick, run_paper_cycle
from app.paper.dlmm_signal import evaluate_canonical_state
from app.paper.engine import PaperEngine
from app.research.grid_runner import evaluate_signal
from app.research.strategy_grid import StrategyConfig
from app.storage.migrations import initialize_database
from app.storage.paper_trades import persist_engine


def canonical_state(*, in_range=True, drain_score=0.1):
    return CanonicalPositionState(
        position_address="POSITION",
        pool_address="POOL",
        observed_at=100.0,
        active_bin_id=100,
        lower_bin_id=90,
        upper_bin_id=110,
        in_range=in_range,
        range_survival_seconds=120.0,
        drain_score=drain_score,
        x_amount=1.0,
        y_amount=1.0,
        x_price_sol=1.0,
        y_price_sol=1.0,
        x_decimals=9,
        y_decimals=9,
        fee_x_delta_raw=1,
        fee_y_delta_raw=1,
        fee_sol=0.01,
        reset_or_claim=False,
        position_value_sol=2.0,
        eligible_for_mtm=True,
        ineligible_reasons=(),
    )


def test_canonical_signal_requires_drain_observation_for_entry():
    signal = evaluate_canonical_state(
        canonical_state(drain_score=None),
        fee_velocity_sol_min=0.02,
        min_fee_velocity=0.01,
    )

    assert signal.entry is False


def test_canonical_signal_exits_out_of_range():
    signal = evaluate_canonical_state(
        canonical_state(in_range=False),
        fee_velocity_sol_min=0.02,
        min_fee_velocity=0.01,
    )

    assert signal.exit is True


def test_cycle_uses_canonical_state_for_entry():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)

    result = run_paper_cycle(
        connection,
        ["POOL"],
        price_by_pool={"POOL": 10.0},
        range_by_pool={"POOL": (9.0, 11.0)},
        market_by_pool={
            "POOL": PaperMarketTick(
                price=10.0,
                fee_delta_sol=0.02,
                fee_velocity_sol_min=0.02,
                drain_score=0.1,
                in_range=True,
            )
        },
        timestamp=100.0,
        canonical_states_by_pool={"POOL": canonical_state()},
    )

    assert result.entries[0].action == "ENTER"
    assert result.opened_pool_addresses == ("POOL",)


def test_cycle_uses_canonical_state_for_exit():
    connection = sqlite3.connect(":memory:")
    initialize_database(connection)
    engine = PaperEngine()
    engine.open("paper:POOL:100", "POOL", 10.0, 9.0, 11.0, 1.0, timestamp=100.0)
    persist_engine(connection, engine)

    result = run_paper_cycle(
        connection,
        [],
        price_by_pool={},
        range_by_pool={},
        market_by_pool={
            "POOL": PaperMarketTick(
                price=10.0,
                fee_delta_sol=0.01,
                fee_velocity_sol_min=0.02,
                drain_score=0.1,
                in_range=True,
            )
        },
        timestamp=110.0,
        canonical_states_by_pool={"POOL": canonical_state(drain_score=0.96)},
    )

    assert result.exits[0].reason == "LIQUIDITY_DRAIN"
    assert result.engine.positions["paper:POOL:100"].status == "CLOSED"


def test_research_grid_config_controls_canonical_signal_thresholds():
    state = canonical_state(drain_score=0.1)
    config = StrategyConfig("S-CANONICAL", 0.8, 0.01, 0.95, 60)

    signal = evaluate_signal(config, state, fee_velocity_sol_min=0.02)

    assert signal.score == 0.73
    assert signal.entry is False
