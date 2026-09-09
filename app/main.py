from __future__ import annotations
import argparse
from datetime import datetime, timezone
from app.meteora.client import MeteoraClient
from app.meteora.pools import select_candidates
from app.storage.database import Database

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-tvl", type=float, default=1000)
    parser.add_argument("--min-volume", type=float, default=10000)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--db", default="data/heart_attack.sqlite3")
    args = parser.parse_args()
    client = MeteoraClient()
    pools = client.iter_pools(
        page_size=1000, sort_by="volume_24h:desc",
        filter_by=f"tvl>={args.min_tvl} && volume_24h>={args.min_volume} && is_blacklisted=false",
    )
    candidates = select_candidates(pools, min_tvl_usd=args.min_tvl, min_volume_24h_usd=args.min_volume)
    db = Database(args.db)
    fetched_at = datetime.now(timezone.utc).isoformat()
    for pool in candidates:
        db.upsert_pool(pool, fetched_at)
    print("Stored", len(candidates), "candidate pools.")
    for pool in candidates[:args.top]:
        print(pool.token_x_symbol + "/" + pool.token_y_symbol,
              "TVL=$" + format(pool.tvl_usd, ",.0f"),
              "24hVol=$" + format(pool.volume_24h_usd, ",.0f"),
              "24hFee=$" + format(pool.fee_24h_usd, ",.0f"),
              "Fee/TVL=" + format(pool.fee_tvl_ratio_24h, ".4f"))
    db.close()

if __name__ == "__main__":
    main()
