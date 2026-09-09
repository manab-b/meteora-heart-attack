from app.collector.price_resolver import TokenPrice, resolve_pair


class Resolver:
    def resolve(self, mint, observed_at):
        prices = {"X": 2.0, "Y": 5.0}
        value = prices.get(mint)
        return None if value is None else TokenPrice(mint, value, observed_at, "test")


def test_resolve_pair_requires_both_quotes():
    pair = resolve_pair(Resolver(), "X", "Y", 100.0)
    assert pair is not None
    assert pair[0].price_usd == 2.0
    assert pair[1].price_usd == 5.0


def test_resolve_pair_returns_none_when_quote_missing():
    assert resolve_pair(Resolver(), "X", "MISSING", 100.0) is None
