from app.strategy.bin_sweep import compare_bin_counts

def test_bin_sweep_has_four_configs():
    result = compare_bin_counts(1.0, 25)
    assert [x.num_bins for x in result] == [3, 5, 7, 9]
    assert all(x.min_price < 1 < x.max_price for x in result)
