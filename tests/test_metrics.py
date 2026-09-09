from app.metrics.drain import liquidity_drain_score
from app.metrics.ranking import score_pool

def test_drain_score():
    assert liquidity_drain_score(100, 40) == 0.6

def test_pool_score_rewards_fee_velocity():
    assert score_pool(0.2, 300, 0.0) > score_pool(0.1, 300, 0.0)
