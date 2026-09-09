from app.research.monte_carlo import bootstrap_trade_pnl


def test_bootstrap_is_reproducible():
    a = bootstrap_trade_pnl([1.0, -0.5, 2.0], runs=200, trades_per_run=20, seed=7)
    b = bootstrap_trade_pnl([1.0, -0.5, 2.0], runs=200, trades_per_run=20, seed=7)
    assert a == b
    assert a.runs == 200
    assert 0.0 <= a.probability_negative <= 1.0
