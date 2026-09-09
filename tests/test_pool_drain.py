from dataclasses import dataclass

import pytest

from app.metrics.pool_drain import aggregate_pool_drain


@dataclass(frozen=True)
class Event:
    pool_address: str
    score: float
    active_bin_moved: bool


def test_pool_drain_uses_strongest_bins():
    events = [
        Event("pool", 0.8, False),
        Event("pool", 0.4, True),
        Event("pool", 0.2, False),
        Event("other", 1.0, False),
    ]
    result = aggregate_pool_drain("pool", events, top_n=2)
    assert result.max_bin_score == pytest.approx(0.8)
    assert result.mean_top_bin_score == pytest.approx(0.6)
    assert result.score == pytest.approx(0.6)
    assert result.event_count == 3
    assert result.active_bin_migration_events == 1


def test_empty_pool_has_zero_drain():
    result = aggregate_pool_drain("pool", [])
    assert result.score == 0.0
    assert result.event_count == 0


def test_top_n_must_be_positive():
    with pytest.raises(ValueError):
        aggregate_pool_drain("pool", [], top_n=0)
