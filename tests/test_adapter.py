from app.positions.adapter import normalize_position

def test_normalize_position():
    p = normalize_position({
        "address": "pos", "owner": "owner", "pool": "pool",
        "lower_bin_id": 1, "upper_bin_id": 7,
        "total_x_amount": "10", "total_y_amount": "20",
        "feeX": "0.1", "feeY": "0.2",
    }, "2026-01-01T00:00:00+00:00")
    assert p.position_address == "pos"
    assert p.unclaimed_fee_x == "0.1"
