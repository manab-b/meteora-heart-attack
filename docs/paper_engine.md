# Heart Attack Paper Engine Specification

## Objective

Evaluate Meteora DLMM liquidity-entry hypotheses without executing real transactions.

## Position lifecycle

OPEN -> TICK* -> CLAIM* -> CLOSED

Exit reasons:
- MANUAL
- OUT_OF_RANGE
- RUG_FLAG

API outages are recorded as data errors and do not imply an exit.

## Core measurements

- entry price/bin
- range width
- current price/bin
- time in range
- time out of range
- observed/estimated fee accumulation
- fee velocity SOL/sec and SOL/min
- price movement
- estimated IL
- fee PnL
- net PnL

## Research protocol

Minimum target: 50 trades.
Preferred: 100+ trades.

Compare:
- new vs existing tokens
- 3/5/7/9 bin ranges
- TVL and volume regimes

Primary metrics:
- median claimed SOL
- fee velocity
- maximum drawdown
- range-out time
- anomaly/rug flag rate

Win rate is not the primary metric.
