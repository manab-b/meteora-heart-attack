from app.collector.meteora_api import MeteoraApiConfig, MeteoraDataApiClient


def test_client_builds_read_only_requests_without_signer(monkeypatch):
    client = MeteoraDataApiClient(
        MeteoraApiConfig(base_url="https://example.invalid", min_request_interval_seconds=0)
    )
    calls: list[tuple[str, dict]] = []

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": [{"address": "POOL"}]}

    def fake_get(path, **kwargs):
        calls.append((path, kwargs))
        return Response()

    monkeypatch.setattr(client._client, "get", fake_get)
    payload = client.get_pools(page=1, page_size=10, sort_by="tvl:desc")
    client.close()

    assert payload["data"][0]["address"] == "POOL"
    assert calls == [("/pools", {"params": {"page": 1, "page_size": 10, "sort_by": "tvl:desc"}})]


def test_ohlcv_params_are_explicit(monkeypatch):
    client = MeteoraDataApiClient(
        MeteoraApiConfig(base_url="https://example.invalid", min_request_interval_seconds=0)
    )
    captured = {}

    class Response:
        def raise_for_status(self):
            return None

        def json(self):
            return {"data": []}

    def fake_get(path, **kwargs):
        captured.update(path=path, **kwargs)
        return Response()

    monkeypatch.setattr(client._client, "get", fake_get)
    client.get_ohlcv("POOL", timeframe="5m", start_time=100, end_time=200)
    client.close()

    assert captured == {
        "path": "/pools/POOL/ohlcv",
        "params": {"timeframe": "5m", "start_time": 100, "end_time": 200},
    }
