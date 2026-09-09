from app.metrics.fee_velocity import FeeObservation, fee_velocity_per_minute

def test_fee_velocity_per_minute():
    a = FeeObservation(0, 0.01)
    b = FeeObservation(30, 0.025)
    assert fee_velocity_per_minute(a, b) == 0.03
