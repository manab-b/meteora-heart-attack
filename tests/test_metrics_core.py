from app.metrics.drain import DrainObservation, liquidity_drain_score
from app.metrics.range_survival import in_bin_range, update_range_survival_seconds
from app.metrics.velocity import FeeVelocity, fee_velocity_sol_min


def test_fee_velocity_uses_position_fee_delta():
    assert fee_velocity_sol_min(0.01, 30) == 0.02
    assert FeeVelocity(0.01, 30).sol_per_minute == 0.02


def test_fee_velocity_invalid_elapsed_is_zero():
    assert fee_velocity_sol_min(0.01, 0) == 0.0


def test_drain_score_and_rate():
    obs = DrainObservation(100_000, 90_000, 30)
    assert obs.drain_score == 0.1
    assert obs.drain_rate_per_minute == 0.2
    assert liquidity_drain_score(100, 80) == 0.2


def test_range_survival_resets_out_of_range():
    assert in_bin_range(105, 100, 110)
    assert update_range_survival_seconds(30, 30, True) == 60
    assert update_range_survival_seconds(60, 30, False) == 0
