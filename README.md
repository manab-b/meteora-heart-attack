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

Meteora's current DLMM SDK exposes both pool-specific position queries and a read-only wallet-wide PositionV2 discovery method. The collector can use the wallet-wide method to find the actual pools where an owner has Meteora positions, avoiding the assumption that an arbitrary pool contains the owner's LP position.

Example environment:

```bash
export RPC_URL="https://YOUR_RPC_ENDPOINT"
export POSITION_OWNER="YOUR_PUBLIC_KEY"
```

Discover all Meteora PositionV2 pools owned by the wallet and collect one snapshot from each discovered pool:

```bash
cd sdk
npm install
npm run collect:positions -- --discover-owner-positions --once
```

For a known pool, collect one position snapshot directly:

```bash
npm run collect:positions -- --once YOUR_POOL_ADDRESS > ../positions.jsonl
```

The discovery mode is read-only: it uses the SDK's owner-position account query and does not require a signer, private key, transaction, claim, swap, or liquidity mutation.

### Global PositionV2 owner discovery

When a candidate wallet has no PositionV2 accounts, the owner-specific SDK query cannot identify another wallet automatically. The SDK also exposes the underlying PositionV2 account layout: the DLMM program stores `lb_pair` at offset 8 and `owner` at offset 40, and the PositionV2 discriminator can be used to filter the program accounts. This repository includes a read-only RPC scanner for that purpose.

```bash
cd sdk
npm run discover:positions -- --rpc-url https://api.mainnet-beta.solana.com --limit 100
```

To verify a specific wallet without relying on the SDK's processed position path:

```bash
npm run discover:positions -- \
  --rpc-url https://api.mainnet-beta.solana.com \
  --owner YOUR_PUBLIC_KEY \
  --limit 100
```

The command only reads Solana `getProgramAccounts` data and returns position addresses, owners and DLMM pool addresses. It does not sign, submit, claim, swap, or mutate liquidity. The global scan may depend on the RPC provider allowing `getProgramAccounts`; use a capable RPC endpoint if the public endpoint rejects large account queries.

Ingest authoritative observations into SQLite:

```bash
cd ..
python -m app.collector.ingest_cli positions.jsonl --db meteora.db
```

For SOL pairs, the ingestion layer automatically records the WSOL side at exactly `1.0 SOL` and values the other side from the same observation's Meteora active-bin UI price. The official WSOL mint is `So11111111111111111111111111111111111111112`.

For non-SOL pairs, no synthetic quote is created; an authoritative token quote must still be supplied.

### Continuous collection + direct SQLite ingest

The runner starts both read-only SDK collectors and writes every valid observation directly into SQLite. No intermediate JSONL files are required:

```bash
python -m app.collector.live_sdk_ingest \
  --rpc-url "$RPC_URL" \
  --position-owner "$POSITION_OWNER" \
  --pool-address "$POOL_ADDRESS" \
  --lower-bin-id "$LOWER_BIN_ID" \
  --upper-bin-id "$UPPER_BIN_ID" \
  --db meteora.db \
  --interval-ms 30000
```

Install the SDK dependencies once before starting it:

```bash
cd sdk
npm install
cd ..
```

The runner keeps raw observations and derived analytics in the same SQLite database, while still refusing to invent missing non-SOL quotes.

For bin liquidity, the standalone collector remains available:

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

## Authoritative SQLite Paper Replay

Replay consumes only persisted position analytics, historical bin prices, drain observations, canonical position state and authoritative token quotes. Missing facts make a point ineligible instead of being estimated.

Replay every persisted position and persist only closed trades with authoritative DLMM PnL:

```bash
python -m app.research.paper_replay_cli meteora.db
```

Replay a selected position:

```bash
python -m app.research.paper_replay_cli meteora.db --position POSITION_ADDRESS
```

Use `--require-paper-trades` when the run must fail unless at least one closed, authoritative paper trade exists. The persisted `paper_trades` records are idempotent for the same strategy/pool/entry/exit timestamps. A closed replay without authoritative PnL is not written as a trade.

## Paper Replay readiness

The replay engine requires authoritative position analytics, bin liquidity/drain observations, historical token quotes, and canonical position state. A dataset that lacks required observations is rejected/left incomplete rather than filled with guessed values.

Local database files are intentionally ignored by Git; they should be supplied to the replay environment rather than committed to the repository.

## Research target

Minimum dataset: 50 paper trades. Preferred: 200+ observations per pool and multiple pool/token categories. Primary outputs are median claimed SOL, fee SOL/min, range survival, liquidity-drain rate, IL, drawdown, walk-forward stability and Monte Carlo tail risk—not win rate alone.
