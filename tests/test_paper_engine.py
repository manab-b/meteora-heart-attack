from app.paper.canonical_position import CanonicalPositionState
from app.paper.engine import PaperEngine


def test_out_of_range_closes_after_threshold():
    e = PaperEngine(out_of_range_seconds=20)
    e.open("p1", "pool", 100, 99, 101, 5)
    e.tick("p1", 102, 0.01, timestamp=0)
    e.tick("p1", 102, 0.01, timestamp=19)
    assert e.positions["p1"].status == "OPEN"
    e.tick("p1", 102, 0, timestamp=20)
    assert e.positions["p1"].status == "CLOSED"


def test_mark_to_market_uses_real_token_snapshot():
    e = PaperEngine()
    e.open(
        "p2", "pool", 100, 99, 101, 5,
        x_amount=2, y_amount=3, x_price_usd=10, y_price_usd=20,
    )
    e.tick(
        "p2", 100, 0, timestamp=10,
        x_amount=1.5, y_amount=4, x_price_usd=12, y_price_usd=18,
    )
    assert e.mark_to_market_usd("p2") == 90.0


def test_mark_to_market_uses_canonical_state_without_estimation():
    e = PaperEngine()
    state = CanonicalPositionState(
        position_address="position",
        pool_address="pool",
        observed_at=60.0,
        active_bin_id=5,
        lower_bin_id=1,
        upper_bin_id=10,
        in_range=True,
        range_survival_seconds=60.0,
        drain_score=0.1,
        x_amount=2.0,
        y_amount=3.0,
        x_price_sol=2.0,
        y_price_sol=3.0,
        x_decimals=3,
        y_decimals=3,
        fee_x_delta_raw=10,
        fee_y_delta_raw=20,
        fee_sol=0.08,
        reset_or_claim=False,
        position_value_sol=13.0,
        eligible_for_mtm=True,
        ineligible_reasons=(),
    )
    assert e.mark_to_market_sol_from_canonical(state) == 13.0


def test_paper_engine_exposes_canonical_dlmm_pnl():
    e = PaperEngine()
    entry = CanonicalPositionState(
        "position", "pool", 0.0, 5, 1, 10, True, 0.0, 0.0,
        1.0, 1.0, 2.0, 1.0, 3, 3, 0, 0, None, False, 3.0, True, (),
    )
    current = CanonicalPositionState(
        "position", "pool", 60.0, 5, 1, 10, True, 60.0, 0.1,
        0.5, 1.4, 3.0, 1.0, 3, 3, 10, 20, 0.1, False, 2.9, True, (),
    )
    result = e.dlmm_pnl_from_canonical(entry, current, fees_sol=0.2)
    assert result.net_pnl_sol == 0.1
    assert result.il_pct < 0


def test_mark_to_market_rejects_ineligible_canonical_state():
    e = PaperEngine()
    state = CanonicalPositionState(
        position_address="position",
        pool_address="pool",
        observed_at=60.0,
        active_bin_id=5,
        lower_bin_id=1,
        upper_bin_id=10,
        in_range=True,
        range_survival_seconds=60.0,
        drain_score=None,
        x_amount=2.0,
        y_amount=3.0,
        x_price_sol=None,
        y_price_sol=3.0,
        x_decimals=3,
        y_decimals=3,
        fee_x_delta_raw=0,
        fee_y_delta_raw=0,
        fee_sol=None,
        reset_or_claim=False,
        position_value_sol=None,
        eligible_for_mtm=False,
        ineligible_reasons=("missing_or_stale_x_price",),
    )
    assert e.mark_to_market_sol_from_canonical(state) is None
