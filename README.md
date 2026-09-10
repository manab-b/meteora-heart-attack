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

The TypeScript collector requires `RPC_URL` and `POSITION_OWNER` and accepts one or more public pool addresses. It emits JSONL observations containing the active bin, UI active-bin price, position range, raw token balances, raw unclaimed fees, claimed-fee totals, token mints and token decimals.

The collector remains strictly read-only. Meteora's current DLMM SDK exposes the same position query and active-bin price conversion used here. citeturn1search0turn1search1

Example environment:

```bash
export RPC_URL="https://YOUR_RPC_ENDPOINT"
export POSITION_OWNER="YOUR_PUBLIC_KEY"
```

Collect one position snapshot for a pool:

```bash
cd sdk
npm install
npm run collect:positions -- --once YOUR_POOL_ADDRESS > ../positions.jsonl
```

Ingest those authoritative observations into SQLite:

```bash
cd ..
python -m app.collector.ingest_cli positions.jsonl --db meteora.db
```

For SOL pairs, the ingestion layer now automatically records the WSOL side at exactly `1.0 SOL` and values the other side from the same observation's Meteora active-bin UI price. The official WSOL mint is `So11111111111111111111111111111111111111112`. citeturn2search0turn2search1

For non-SOL pairs, no synthetic quote is created; an authoritative token quote must still be supplied.

For bin liquidity, set the same `RPC_URL` plus the public pool and observed position range, then collect and ingest:

```bash
export POOL_ADDRESS="YOUR_POOL_ADDRESS"
export LOWER_BIN_ID="LOWER_BIN_ID"
export UPPER_BIN_ID="UPPER_BIN_ID"
cd sdk
npm run collect:bins > ../bins.jsonl
cd ..
python -m app.collector.bin_ingest_cli bins.jsonl --db meteora.db
```

Repeat the read-only collection over time to build the historical observation series required by Paper Replay. The collectors do not load a signer or construct/send transactions. Do not replace missing observations with estimates.

## Paper Replay readiness

The replay engine requires authoritative position analytics, bin liquidity/drain observations, historical token quotes, and canonical position state. A dataset that lacks required observations is rejected/left incomplete rather than filled with guessed values.

Local database files are intentionally ignored by Git; they should be supplied to the replay environment rather than committed to the repository.

## Research target

Minimum dataset: 50 paper trades. Preferred: 200+ observations per pool and multiple pool/token categories. Primary outputs are median claimed SOL, fee SOL/min, range survival, liquidity-drain rate, IL, drawdown, walk-forward stability and Monte Carlo tail risk—not win rate alone.
