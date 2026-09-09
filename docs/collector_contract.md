# Collector contract

Adapters normalize external data into PoolSnapshot, BinSnapshot and PositionSnapshot.

The collector preserves source timestamps and never invents unavailable fields. The initial paper cadence is 30 seconds.

Quality checks reject non-positive prices, invalid timestamps, stale observations and implausibly future-dated observations.

Pool-wide volume is used for discovery/filtering only. Position-level fee fields remain authoritative for fee accumulation.
