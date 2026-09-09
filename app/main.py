from __future__ import annotations

import argparse
from datetime import datetime, timezone

from app.collector.live_readonly import collect_top_pools_readonly
from app.collector.meteora_api import MeteoraApiConfig, MeteoraDataApiClient
from app.meteora.client import MeteoraClient
from app.meteora.pools import select_candidates
from app.storage.database import Database
from app.storage.migrations import initialize_database


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--min-tvl", type=float, default=1000)
    parser.add_argument("--min-volume", type=float, default=10000)
    parser.add_argument("--top", type=int, default=20)
    parser.add_argument("--db", default="data/heart_attack.sqlite3")
    parser.add_argument("--collect-raw", action="store_true", help="fetch real Meteora API payloads and persist them")
    parser.add_argument("--collect-limit", type=int, default=5)
    parser.add_argument("--page-size", type=int, default=100)
    parser.add_argument("--timeframe", default="5m")
    args = parser.parse_args()

    if args.collect_raw:
        db = Database(args.db)
        initialize_database(db.connection)
        with MeteoraDataApiClient(MeteoraApiConfig()) as client:
            result = collect_top_pools_readonly(
                db.connection,
                client,
                limit=args.collect_limit,
                page_size=args.page_size,
                timeframe=args.timeframe,
            )
        db.close()
        print(
            "Readonly collection:",
            f"discovered={result.discovered}",
            f"attempted={result.attempted}",
            f"succeeded={result.succeeded}",
            f"failed={result.failed}",
        )
        return

    client = MeteoraClient()
    pools = client.iter_pools(
        page_size=1000,
        sort_by="volume_24h:desc",
        filter_by=f"tvl>={args.min_tvl} && volume_24h>={args.min_volume} && is_blacklisted=false",
    )
    candidates = select_candidates(
        pools,
        min_tvl_usd=args.min_tvl,
        min_volume_24h_usd=args.min_volume,
    )
    db = Database(args.db)
    fetched_at = datetime.now(timezone.utc).isoformat()
    for pool in candidates:
        db.upsert_pool(pool, fetched_at)
    print("Stored", len(candidates), "candidate pools.")
    for pool in candidates[:args.top]:
        print(
            pool.token_x_symbol + "/" + pool.token_y_symbol,
            "TVL=$" + format(pool.tvl_usd, ",.0f"),
            "24hVol=$" + format(pool.volume_24h_usd, ",.0f"),
            "24hFee=$" + format(pool.fee_24h_usd, ",.0f"),
            "Fee/TVL=" + format(pool.fee_tvl_ratio_24h, ".4f"),
        )
    db.close()


if __name__ == "__main__":
    main()
