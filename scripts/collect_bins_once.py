from __future__ import annotations

import argparse
import os
import sqlite3
import subprocess
import sys
from pathlib import Path

# Allow direct execution from the repository root (e.g. `python scripts/...py`).
ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from app.collector.bin_ingest import ingest_jsonl
from app.storage.migrations import initialize_database


def main() -> int:
    parser = argparse.ArgumentParser(
        description="One-shot real Meteora bin collection through the existing SDK collector, then ingest its JSONL into SQLite."
    )
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--pool-address", required=True)
    parser.add_argument("--lower-bin-id", required=True, type=int)
    parser.add_argument("--upper-bin-id", required=True, type=int)
    parser.add_argument("--db", type=Path, default=Path("meteora.db"))
    parser.add_argument("--sdk-dir", type=Path, default=Path("sdk"))
    args = parser.parse_args()

    if args.lower_bin_id > args.upper_bin_id:
        parser.error("--lower-bin-id must be <= --upper-bin-id")

    sdk_dir = args.sdk_dir.resolve()
    sdk_bin = sdk_dir / "node_modules" / ".bin" / "tsx"
    if not sdk_bin.exists():
        raise SystemExit(f"tsx executable not found: {sdk_bin}. Run npm install in {sdk_dir} first.")

    env = os.environ.copy()
    env.update(
        {
            "RPC_URL": args.rpc_url,
            "POOL_ADDRESS": args.pool_address,
            "LOWER_BIN_ID": str(args.lower_bin_id),
            "UPPER_BIN_ID": str(args.upper_bin_id),
            "COLLECT_INTERVAL_MS": "1",
        }
    )

    process = subprocess.run(
        [str(sdk_bin), "src/bin_collector.ts", "--once"],
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
        print("ERROR: one-shot Meteora bin collection returned zero JSONL observations", file=sys.stderr)
        return 2

    args.db.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(args.db)
    try:
        initialize_database(connection)
        count = ingest_jsonl(connection, lines)
    finally:
        connection.close()

    print(f"bin_observations_ingested={count}")
    if count == 0:
        print("ERROR: one-shot Meteora bin collection produced no ingestible observations", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
