from app.scanner.rank import Candidate, rank

def test_rank_prefers_fee():
    xs = [
        Candidate("a", 1, .02, 300, 0),
        Candidate("b", 1, .10, 300, 0),
    ]
    assert rank(xs)[0].pool_address == "b"
