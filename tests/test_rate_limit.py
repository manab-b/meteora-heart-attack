from app.collector.rate_limit import RateLimiter

def test_rate_limiter_rejects_invalid_rate():
    try:
        RateLimiter(0)
        assert False
    except ValueError:
        assert True
