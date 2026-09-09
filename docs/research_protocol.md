# Research protocol

The scanner first filters stale or economically irrelevant pools. Candidates then receive bin configurations for 3/5/7/9 bins. Each configuration is evaluated on the same observation stream.

Primary metrics:
- median claimed SOL
- SOL/min
- range survival
- liquidity drain rate
- IL
- max drawdown
- exit reason distribution

A pool-wide volume metric is never used as a substitute for position-level unclaimed fees.

Meteora's current DLMM Data API exposes pools, OHLCV, volume history, portfolio and position history/PnL endpoints, while the official SDK exposes position and fee operations. The SDK examples also document read-side position access patterns. citeturn0search0turn0search1
