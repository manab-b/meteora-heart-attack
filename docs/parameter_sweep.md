# Parameter sweep

The research engine now evaluates bin count and entry/exit thresholds systematically.

Do not select a configuration solely by total fee. Require a minimum trade count and inspect:
- median fee per trade
- fee per minute
- range survival
- drain exits
- fee-decay exits
- out-of-range exits
- IL and drawdown from the valuation layer

The default sweep is deliberately small enough for fast iteration. Once the replay dataset is populated, expand the grid and use out-of-sample validation rather than choosing parameters on the full sample.
