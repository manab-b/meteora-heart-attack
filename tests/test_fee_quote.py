from app.valuation.fee_quote import FeeQuote, quote_fee_delta


def test_quote_fee_delta_requires_both_prices():
    assert quote_fee_delta(
        fee_x_raw="1000000",
        fee_y_raw="2000000",
        x_decimals=6,
        y_decimals=6,
        x_sol_price=None,
        y_sol_price=0.01,
    ) is None


def test_quote_fee_delta_converts_raw_amounts():
    value = quote_fee_delta(
        fee_x_raw="1000000",
        fee_y_raw="2000000",
        x_decimals=6,
        y_decimals=6,
        x_sol_price=0.5,
        y_sol_price=0.25,
    )
    assert value == 1.0


def test_fee_quote_dataclass():
    quote = FeeQuote(
        fee_x_raw=1_000_000,
        fee_y_raw=2_000_000,
        x_decimals=6,
        y_decimals=6,
        x_sol_price=0.5,
        y_sol_price=0.25,
        observed_at=100.0,
        source="test",
    )
    assert quote.value_sol() == 1.0
