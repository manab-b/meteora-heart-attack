from app.research.walkforward import split_observations

def test_split():
    a,b = split_observations(list(range(10)), .7)
    assert len(a) == 7
    assert len(b) == 3
