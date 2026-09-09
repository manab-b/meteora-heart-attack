from app.paper.engine import PaperEngine

def test_out_of_range_closes_after_threshold():
    e = PaperEngine(out_of_range_seconds=20)
    e.open("p1", "pool", 100, 99, 101, 5)
    e.tick("p1", 102, 0.01, timestamp=0)
    e.tick("p1", 102, 0.01, timestamp=19)
    assert e.positions["p1"].status == "OPEN"
    e.tick("p1", 102, 0, timestamp=20)
    assert e.positions["p1"].status == "CLOSED"
