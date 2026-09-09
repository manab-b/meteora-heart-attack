from datetime import datetime, timezone
from app.collector.quality import validate_snapshot

def test_rejects_bad_price():
    r = validate_snapshot(0, datetime.now(timezone.utc).isoformat())
    assert not r.valid
    assert "NON_POSITIVE_PRICE" in r.reasons

def test_accepts_fresh_price():
    r = validate_snapshot(1, datetime.now(timezone.utc).isoformat())
    assert r.valid
