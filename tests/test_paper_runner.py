import sqlite3

from app.paper.engine import PaperEngine
from app.scanner.paper_runner import apply_entry_decisions, evaluate_paper_exit
from app.strategy.exit import ExitConfig


def test_paper_exit_uses_existing_exit_rules():
    decision = evaluate_paper_exit(
        in_range=True,
        out_of_range_seconds=0,
        drain_score=0.8,
        fee_velocity_sol_min=0.1,
        exit_config=ExitConfig(max_drain_score=0.7),
    )
    assert decision is not None
    assert decision.action == "EXIT"
    assert decision.reason == "LIQUIDITY_DRAIN"


def test_apply_entry_decisions_opens_paper_position():
    engine = PaperEngine()
    from app.scanner.paper_runner import PaperDecision

    opened = apply_entry_decisions(
        engine,
        [PaperDecision("POOL", "ENTER")],
        price_by_pool={"POOL": 10.0},
        range_by_pool={"POOL": (9.0, 11.0)},
        timestamp=100.0,
    )
    assert opened == ["POOL"]
    assert engine.positions["paper:POOL:100.0"].status == "OPEN"
