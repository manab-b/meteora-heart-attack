import pytest

from app.metrics.bin_liquidity import BinLiquiditySnapshot, bin_removed, liquidity_change_ratio


def test_liquidity_change_ratio():
    previous = BinLiquiditySnapshot(10, 700, 300, 100.0)
    current = BinLiquiditySnapshot(10, 350, 150, 130.0)
    assert liquidity_change_ratio(previous, current) == 0.5


def test_bin_removed():
    previous = BinLiquiditySnapshot(10, 1, 2, 100.0)
    current = BinLiquiditySnapshot(10, 0, 0, 130.0)
    assert bin_removed(previous, current)


def test_different_bins_rejected():
    with pytest.raises(ValueError):
        liquidity_change_ratio(
            BinLiquiditySnapshot(10, 1, 1, 1.0),
            BinLiquiditySnapshot(11, 1, 1, 2.0),
        )
