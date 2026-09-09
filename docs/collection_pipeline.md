# Collection Pipeline

REST discovers candidate pools. The official Meteora TypeScript SDK then samples active-bin state every 30 seconds. Each sample includes the active bin and nearby bins. JSONL output is suitable for a downstream ingester.

The collector is read-only and never signs transactions.

The Meteora Data API is an indexed read-only layer with a 30 RPS limit. The official SDK exposes direct pool-state reads including getActiveBin and getBinsAroundActiveBin.

Pool-wide volume must not be treated as an individual LP's unclaimed fee. Position-level fee state is the next data source to integrate.
