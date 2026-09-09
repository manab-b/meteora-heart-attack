# Meteora API Data Contract

This document records the data contract for the research engine. API fields must be verified against the live Meteora response before implementation relies on them.

## REST

Primary DLMM Data API:
https://dlmm.datapi.meteora.ag

Planned data sources:
- pool discovery/details
- pool metrics
- OHLCV
- historical volume

Data provenance is classified as ACTUAL, ESTIMATED, or UNAVAILABLE.

## On-chain / SDK

For sub-minute research, REST history alone is not sufficient. Active-bin and bin-level state should be obtained through the Meteora DLMM SDK/RPC path when required.

Planned fields:
- active bin
- bin step
- bin liquidity around the active bin
- position state
- fee X / fee Y where position-level data is available

## Tick contract

timestamp
pool_address
token
price_usd
sol_price_usd
volume_usd
volume_in_range_usd
active_bin
tvl_usd
unclaimed_fees_usd
data_timestamp
received_timestamp
out_of_range_seconds
rug_flags

Unavailable values must be null rather than fabricated.

## Collection policy

Default polling interval: 30 seconds.
The collector must handle HTTP errors without converting them into exits, record stale data, respect rate limits, and use UTC internally.
