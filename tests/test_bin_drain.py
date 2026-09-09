import pytest

from app.metrics.bin_drain import classify_bin_drain


def test_bin_depletion_is_strong_when_active_bin_is_stable():
    signal = classify_bin_drain(
        pool_address="pool",
        bin_id=100,
        previous_active_bin_id=100,
        current_active_bin_id=100,
        previous_x_raw=800,
        previous_y_raw=200,
        current_x_raw=400,
        current_y_raw=100,
        elapsed_seconds=30,
    )
    assert signal.depletion_ratio == pytest.approx(0.5)
    assert signal.score == pytest.approx(0.5)


def test_bin_depletion_is_discounted_during_bin_migration():
    signal = classify_bin_drain(
        pool_address="pool",
        bin_id=100,
        previous_active_bin_id=100,
        current_active_bin_id=101,
        previous_x_raw=800,
        previous_y_raw=200,
        current_x_raw=400,
        current_y_raw=100,
        elapsed_seconds=30,
    )
    assert signal.score == pytest.approx(0.175)


def test_elapsed_must_be_positive():
    with pytest.raises(ValueError):
        classify_bin_drain(
            pool_address="pool",
            bin_id=100,
            previous_active_bin_id=100,
            current_active_bin_id=100,
            previous_x_raw=1,
            previous_y_raw=1,
            current_x_raw=0,
            current_y_raw=0,
            elapsed_seconds=0,
        )
