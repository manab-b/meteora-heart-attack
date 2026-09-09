from app.meteora.client import MeteoraClient

def test_iter_pools_paginates():
    client = MeteoraClient()
    responses = [
        {"data":[{"address":"A"}],"pages":2},
        {"data":[{"address":"B"}],"pages":2},
    ]
    client.list_pools = lambda **kwargs: responses[kwargs["page"] - 1]
    assert [p["address"] for p in client.iter_pools(page_size=100)] == ["A", "B"]
