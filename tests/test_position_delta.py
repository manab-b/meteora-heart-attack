from app.positions.model import PositionSnapshot
from app.positions.delta import calculate_fee_delta

def snap(t, x, y):
    return PositionSnapshot("pos", "owner", "pool", 1, 7, "1", "2",
                             str(x), str(y), t, "test")

def test_fee_delta_per_minute():
    a = snap("2026-01-01T00:00:00+00:00", 1.0, 2.0)
    b = snap("2026-01-01T00:00:30+00:00", 1.1, 2.2)
    d = calculate_fee_delta(a, b)
    assert d.fee_x_per_minute == 0.2
    assert d.fee_y_per_minute == 0.4
