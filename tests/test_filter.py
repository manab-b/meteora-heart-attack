from app.scanner.filter import eligible_pool

def test_pool_filter():
    assert eligible_pool(20_000, 100_000, 200, 30)
    assert not eligible_pool(20_000, 100_000, 200, 300)
