from app.scanner.opportunity import build_rows

def test_best_bin_configuration_is_first():
    rows = build_rows("pool", {3:.02,5:.05,7:.03}, {3:300,5:300,7:300}, 0)
    assert rows[0].bins == 5
