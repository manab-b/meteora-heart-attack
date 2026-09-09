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
