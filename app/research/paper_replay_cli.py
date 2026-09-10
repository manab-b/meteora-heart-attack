from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path

from app.research.paper_replay import replay_all_positions, replay_position


_REQUIRED_TABLES = (
    "position_analytics",
    "position_snapshots",
    "bin_liquidity_snapshots",
    "bin_drain_events",
    "token_quotes",
    "raw_snapshots",
)


def _validate_database(connection: sqlite3.Connection) -> None:
    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table'"
    ).fetchall()
    available = {row[0] for row in rows}
    missing = [name for name in _REQUIRED_TABLES if name not in available]
    if missing:
        raise ValueError(
            "database is missing required authoritative tables: " + ", ".join(missing)
        )


def _result_payload(result) -> dict:
    closed = result.closed
    payload = {
        "position_address": result.position_address,
        "pool_address": result.pool_address,
        "observations": len(result.points),
        "closed": closed,
        "events": list(result.events),
        "skipped": list(result.skipped),
        "paper_trade": closed,
    }
    if result.dlmm_pnl is not None:
        payload["dlmm_pnl"] = {
            "entry_value_sol": result.dlmm_pnl.entry_value_sol,
            "current_value_sol": result.dlmm_pnl.current_value_sol,
            "fees_sol": result.dlmm_pnl.fees_sol,
            "net_pnl_sol": result.dlmm_pnl.net_pnl_sol,
        }
    else:
        payload["dlmm_pnl"] = None
    return payload


def run(
    db_path: str | Path,
    *,
    position_address: str | None = None,
    deposit_sol: float = 1.0,
    out_of_range_seconds: int = 20,
    max_drain_score: float = 0.95,
    min_fee_velocity_sol_min: float = 0.0,
    min_score: float = 0.7,
    require_paper_trades: bool = False,
) -> dict:
    path = Path(db_path)
    if not path.is_file():
        raise FileNotFoundError(f"SQLite database not found: {path}")

    with sqlite3.connect(path) as connection:
        _validate_database(connection)
        if position_address:
            results = (
                replay_position(
                    connection,
                    position_address=position_address,
                    deposit_sol=deposit_sol,
                    out_of_range_seconds=out_of_range_seconds,
                    max_drain_score=max_drain_score,
                    min_fee_velocity_sol_min=min_fee_velocity_sol_min,
                    min_score=min_score,
                ),
            )
        else:
            results = replay_all_positions(
                connection,
                deposit_sol=deposit_sol,
                out_of_range_seconds=out_of_range_seconds,
                max_drain_score=max_drain_score,
                min_fee_velocity_sol_min=min_fee_velocity_sol_min,
                min_score=min_score,
            )

    trades = [_result_payload(result) for result in results]
    closed = sum(item["paper_trade"] for item in trades)
    if require_paper_trades and closed == 0:
        raise ValueError("replay produced no closed paper trades")

    return {
        "database": str(path),
        "positions_replayed": len(trades),
        "paper_trades": closed,
        "results": trades,
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Replay persisted Meteora observations as read-only paper trades."
    )
    parser.add_argument("database", help="path to the persisted SQLite database")
    parser.add_argument("--position", dest="position_address")
    parser.add_argument("--deposit-sol", type=float, default=1.0)
    parser.add_argument("--out-of-range-seconds", type=int, default=20)
    parser.add_argument("--max-drain-score", type=float, default=0.95)
    parser.add_argument("--min-fee-velocity-sol-min", type=float, default=0.0)
    parser.add_argument("--min-score", type=float, default=0.7)
    parser.add_argument(
        "--require-paper-trades",
        action="store_true",
        help="fail unless the replay produces at least one closed paper trade",
    )
    args = parser.parse_args()

    payload = run(
        args.database,
        position_address=args.position_address,
        deposit_sol=args.deposit_sol,
        out_of_range_seconds=args.out_of_range_seconds,
        max_drain_score=args.max_drain_score,
        min_fee_velocity_sol_min=args.min_fee_velocity_sol_min,
        min_score=args.min_score,
        require_paper_trades=args.require_paper_trades,
    )
    print(json.dumps(payload, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
