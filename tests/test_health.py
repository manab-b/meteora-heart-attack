from app.metrics.il import impermanent_loss_pct
from app.metrics.health import health_score

def test_il_is_zero_at_entry():
    assert impermanent_loss_pct(100, 100) == 0

def test_health_prefers_fee_and_survival():
    assert health_score(0.2, 0, 300, 0) > health_score(0.1, 0, 60, 0)
