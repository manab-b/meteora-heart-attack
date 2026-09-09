# Meteora Heart Attack

Read-only research and paper-trading engine for Meteora DLMM pools.

## Pipeline

REST pool discovery -> SDK/RPC bin observations -> read-only position snapshots -> raw fee deltas -> bin-based range survival -> token valuation -> IL/PnL -> paper execution -> walk-forward -> Monte Carlo.

No private keys, transaction signing, claims, swaps, or liquidity mutations are required.

## Principles

- Do not infer position-level fees from pool-wide volume.
- Do not fabricate unavailable fields or token/SOL prices.
- Keep raw observations and derived metrics separate.
- Keep raw token amounts as strings until decimals are known.
- Treat negative cumulative-fee deltas as claim/reset events, never as negative earned fees.
- Use active bin IDs for DLMM range truth when available.
- Use paper execution until the dataset validates the strategy.

## Current modules

- `app/meteora`: REST pool discovery.
- `app/collector`: REST collection and SDK JSONL ingestion.
- `sdk`: read-only Meteora DLMM SDK collectors.
- `app/positions`: position snapshots, raw fee deltas and bin-based range analytics.
- `app/valuation`: decimal-aware token valuation with explicit SOL pricing.
- `app/metrics`: fee velocity, range, drain, IL and position PnL.
- `app/paper`: deterministic paper position engine.
- `app/research`: parameter sweep, walk-forward selection and bootstrap Monte Carlo.
- `app/storage`: SQLite persistence for raw, position and derived observations.

## Read-only position collection

The TypeScript collector requires `RPC_URL` and `POSITION_OWNER` and accepts one or more pool addresses. It emits JSONL observations containing the active bin, position range, raw token balances, raw unclaimed fees, claimed-fee totals and token decimals.

Example environment:

```bash
export RPC_URL="https://YOUR_RPC_ENDPOINT"
export POSITION_OWNER="YOUR_PUBLIC_KEY"
```

Then run the SDK collector. The collector does not load a signer or construct/send transactions.

## Research target

Minimum dataset: 50 paper trades. Preferred: 200+ observations per pool and multiple pool/token categories. Primary outputs are median claimed SOL, fee SOL/min, range survival, liquidity-drain rate, IL, drawdown, walk-forward stability and Monte Carlo tail risk—not win rate alone.
