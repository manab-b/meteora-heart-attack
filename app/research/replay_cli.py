from __future__ import annotations

import argparse
import json
import sqlite3

from app.research.paper_replay import persist_replay_results, replay_all_positions
from app.storage.migrations import initialize_database


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Replay persisted authoritative Meteora observations as paper trades."
    )
    parser.add_argument("--db", required=True, help="SQLite database containing collected observations")
    parser.add_argument("--position", action="append", dest="positions", help="Replay only this position address; repeatable")
    parser.add_argument("--deposit-sol", type=float, default=1.0)
    parser.add_argument("--out-of-range-seconds", type=int, default=20)
    parser.add_argument("--max-drain-score", type=float, default=0.95)
    parser.add_argument("--min-fee-velocity-sol-min", type=float, default=0.0)
    parser.add_argument("--min-score", type=float, default=0.7)
    parser.add_argument("--strategy-key", default="canonical-heart-attack-replay")
    parser.add_argument("--no-persist", action="store_true", help="Do not write closed replay trades to paper_trades")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    if args.deposit_sol <= 0:
        raise SystemExit("--deposit-sol must be positive")
    if args.out_of_range_seconds < 0:
        raise SystemExit("--out-of-range-seconds must be non-negative")
    if not 0.0 <= args.max_drain_score <= 1.0:
        raise SystemExit("--max-drain-score must be between 0 and 1")
    if args.min_fee_velocity_sol_min < 0:
        raise SystemExit("--min-fee-velocity-sol-min must be non-negative")
    if not 0.0 <= args.min_score <= 1.0:
        raise SystemExit("--min-score must be between 0 and 1")

    conn = sqlite3.connect(args.db)
    try:
        initialize_database(conn)
        if args.positions:
            results = tuple(
                replay_all_positions(
                    conn,
                    deposit_sol=args.deposit_sol,
                    out_of_range_seconds=args.out_of_range_seconds,
                    max_drain_score=args.max_drain_score,
                    min_fee_velocity_sol_min=args.min_fee_velocity_sol_min,
                    min_score=args.min_score,
                )[0:0]
            )
            # Replay the explicitly requested positions without changing the shared replay implementation.
            from app.research.paper_replay import replay_position
            results = tuple(
                replay_position(
                    conn,
                    position_address=position,
                    deposit_sol=args.deposit_sol,
                    out_of_range_seconds=args.out_of_range_seconds,
                    max_drain_score=args.max_drain_score,
                    min_fee_velocity_sol_min=args.min_fee_velocity_sol_min,
                    min_score=args.min_score,
                )
                for position in args.positions
            )
        else:
            results = replay_all_positions(
                conn,
                deposit_sol=args.deposit_sol,
                out_of_range_seconds=args.out_of_range_seconds,
                max_drain_score=args.max_drain_score,
                min_fee_velocity_sol_min=args.min_fee_velocity_sol_min,
                min_score=args.min_score,
            )

        persisted = 0 if args.no_persist else persist_replay_results(
            conn, results, strategy_key=args.strategy_key
        )
        closed = sum(result.closed for result in results)
        print(json.dumps({
            "positions": len(results),
            "closed": closed,
            "persisted_trades": persisted,
            "results": [
                {
                    "position_address": result.position_address,
                    "pool_address": result.pool_address,
                    "points": len(result.points),
                    "closed": result.closed,
                    "events": list(result.events),
                    "skipped": list(result.skipped),
                    "dlmm_pnl": None if result.dlmm_pnl is None else {
                        "entry_value_sol": result.dlmm_pnl.entry_value_sol,
                        "current_value_sol": result.dlmm_pnl.current_value_sol,
                        "hodl_value_sol": result.dlmm_pnl.hodl_value_sol,
                        "fees_sol": result.dlmm_pnl.fees_sol,
                        "il_pct": result.dlmm_pnl.il_pct,
                        "net_pnl_sol": result.dlmm_pnl.net_pnl_sol,
                        "net_return_pct": result.dlmm_pnl.net_return_pct,
                    },
                }
                for result in results
            ],
        }, sort_keys=True))
        return 0
    finally:
        conn.close()


if __name__ == "__main__":
    raise SystemExit(main())
