from app.metrics.bin_drain_history import BinLiquidityPoint, compare_bin_snapshots, compare_history


def point(ts: float, x: int, y: int, active: int = 10, bin_id: int = 9) -> BinLiquidityPoint:
    return BinLiquidityPoint("pool", bin_id, active, x, y, ts)


def test_compare_bin_snapshots_detects_depletion():
    event = compare_bin_snapshots(point(0, 100, 100), point(30, 50, 100))
    assert event.elapsed_seconds == 30
    assert event.depletion_ratio == 0.25
    assert event.score == 0.25
    assert event.active_bin_moved is False


def test_active_bin_move_discounts_score():
    event = compare_bin_snapshots(point(0, 100, 100, active=10), point(30, 50, 100, active=11))
    assert event.active_bin_moved is True
    assert event.score == 0.0875


def test_compare_history_groups_and_sorts():
    events = compare_history(
        [
            point(60, 50, 50),
            point(30, 75, 50),
            point(0, 100, 50),
            point(0, 200, 0, bin_id=8),
            point(30, 100, 0, bin_id=8),
        ]
    )
    assert len(events) == 3
    assert [(e.bin_id, e.observed_at) for e in events] == [(8, 30), (9, 30), (9, 60)]


def test_compare_rejects_different_pool_or_bin():
    try:
        compare_bin_snapshots(point(0, 1, 1), BinLiquidityPoint("other", 9, 10, 1, 1, 30))
    except ValueError as exc:
        assert "pool_address" in str(exc)
    else:
        raise AssertionError("expected pool mismatch")
