from app.meteora.pools import select_candidates

def test_select_candidates_filters_and_ranks():
    pools = [
        {"address":"A","name":"A","tvl":5000,"volume":{"24h":100000},"fees":{"24h":1000},
         "fee_tvl_ratio":{"24h":0.20},"current_price":1,"dynamic_fee_pct":0.1,
         "pool_config":{"bin_step":25},"is_blacklisted":False,"token_x":{"symbol":"X"},"token_y":{"symbol":"Y"}},
        {"address":"B","name":"B","tvl":500,"volume":{"24h":100000},"fees":{"24h":1000},
         "fee_tvl_ratio":{"24h":0.50},"current_price":1,"dynamic_fee_pct":0.1,
         "pool_config":{"bin_step":25},"is_blacklisted":False,"token_x":{"symbol":"X"},"token_y":{"symbol":"Y"}},
    ]
    result = select_candidates(pools, min_tvl_usd=1000, min_volume_24h_usd=10000)
    assert [p.address for p in result] == ["A"]
