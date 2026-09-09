from app.collector.endpoints import MeteoraDataApi


class FakeLimiter:
    def wait(self):
        pass


class FakeClient:
    def __init__(self):
        self.calls = []

    def get_json(self, path, params=None):
        self.calls.append((path, params))
        return {"ok": True}


def test_pool_endpoint():
    client = FakeClient()
    api = MeteoraDataApi(client)
    api.limiter = FakeLimiter()
    assert api.pool("POOL") == {"ok": True}
    assert client.calls == [("/pools/POOL", None)]


def test_history_endpoints_forward_params():
    client = FakeClient()
    api = MeteoraDataApi(client)
    api.limiter = FakeLimiter()
    api.ohlcv("POOL", timeframe="1h", start=100, end=200)
    api.volume_history("POOL", timeframe="30m")
    assert client.calls == [
        ("/pools/POOL/ohlcv", {"timeframe": "1h", "start": "100", "end": "200"}),
        ("/pools/POOL/volume/history", {"timeframe": "30m"}),
    ]
