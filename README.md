# Meteora Heart Attack

Read-only research and paper-trading engine for Meteora DLMM pools.

## Pipeline

REST pool discovery -> SDK/RPC bin observations -> position snapshots -> fee deltas -> range/drain/IL metrics -> paper execution -> opportunity ranking.

No private keys or transaction signing are required.

## Principles

- Do not infer position-level fees from pool-wide volume.
- Do not fabricate unavailable fields.
- Keep raw observations and derived metrics separate.
- Use paper execution until the dataset validates the strategy.

## Current modules

- `app/meteora`: REST pool discovery.
- `app/collector`: observation models and REST collection.
- `sdk`: read-only Meteora DLMM SDK collector.
- `app/positions`: position snapshot and fee-delta models.
- `app/metrics`: fee velocity, range, drain, IL and health scoring.
- `app/paper`: paper position engine.
- `app/storage`: SQLite persistence.

## Research target

Minimum dataset: 50 paper trades. Preferred: 200+ observations per pool and multiple pool/token categories. Primary outputs are median claimed SOL, fee SOL/min, range survival, liquidity-drain rate, IL, and drawdown—not win rate alone.
