from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

from app.collector.position_ingest import ingest_jsonl
from app.storage.migrations import initialize_database


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-shot real Meteora position collection through the existing SDK collector, then ingest its JSONL into SQLite."
    )
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--position-owner", required=True)
    pool_group = parser.add_mutually_exclusive_group(required=True)
    pool_group.add_argument("--pool-address")
    pool_group.add_argument(
        "--discover-owner-positions",
        action="store_true",
        help="Discover all Meteora PositionV2 pools owned by --position-owner using the SDK."
    )
    parser.add_argument("--db", type=Path, default=Path("meteora.db"))
    parser.add_argument("--sdk-dir", type=Path, default=Path("sdk"))
    args = parser.parse_args()

    sdk_dir = args.sdk_dir.resolve()
    sdk_bin = sdk_dir / "node_modules" / ".bin" / "tsx"
    if not sdk_bin.exists():
        raise SystemExit(f"tsx executable not found: {sdk_bin}. Run npm install in {sdk_dir} first.")

    env = os.environ.copy()
    env.update(
        {
            "RPC_URL": args.rpc_url,
            "POSITION_OWNER": args.position_owner,
            "COLLECT_INTERVAL_MS": "1",
            "COLLECT_ONCE": "1",
            "DISCOVER_OWNER_POSITIONS": "1" if args.discover_owner_positions else "0",
        }
    )

    collector_args = [str(sdk_bin), "src/position_collector.ts"]
    if not args.discover_owner_positions:
        collector_args.append(args.pool_address)

    process = subprocess.run(
        collector_args,
        cwd=sdk_dir,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )

    if process.stderr:
        print(process.stderr, file=sys.stderr, end="")
    if process.returncode != 0:
        return process.returncode

    lines = [line for line in process.stdout.splitlines() if line.strip()]
    if not lines:
        print("ERROR: one-shot Meteora position collection returned zero JSONL observations", file=sys.stderr)
        return 2

    args.db.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(args.db)
    try:
        initialize_database(connection)
        results = ingest_jsonl(connection, lines)
    finally:
        connection.close()

    print(f"position_observations_ingested={len(results)}")
    if not results:
        print("ERROR: one-shot Meteora position collection produced no ingestible observations", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
