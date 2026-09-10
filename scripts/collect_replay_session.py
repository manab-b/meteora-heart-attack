from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path


ROOT_DIR = Path(__file__).resolve().parents[1]
POSITION_SCRIPT = ROOT_DIR / "scripts" / "collect_positions_once.py"
BIN_SCRIPT = ROOT_DIR / "scripts" / "collect_bins_once.py"


def run_once(command: list[str]) -> int:
    process = subprocess.run(command, cwd=ROOT_DIR, check=False)
    return process.returncode


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Run bounded real Meteora Position + Bin one-shot collection cycles "
            "and persist every cycle directly into the existing SQLite database."
        )
    )
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--position-owner", required=True)
    parser.add_argument("--pool-address", required=True)
    parser.add_argument("--lower-bin-id", required=True, type=int)
    parser.add_argument("--upper-bin-id", required=True, type=int)
    parser.add_argument("--duration-seconds", required=True, type=float)
    parser.add_argument("--interval-seconds", type=float, default=30.0)
    parser.add_argument("--db", type=Path, default=Path("meteora.db"))
    parser.add_argument("--sdk-dir", type=Path, default=Path("sdk"))
    args = parser.parse_args()

    if args.lower_bin_id > args.upper_bin_id:
        parser.error("--lower-bin-id must be <= --upper-bin-id")
    if args.duration_seconds <= 0:
        parser.error("--duration-seconds must be > 0")
    if args.interval_seconds <= 0:
        parser.error("--interval-seconds must be > 0")

    python = sys.executable
    position_command = [
        python,
        str(POSITION_SCRIPT),
        "--rpc-url",
        args.rpc_url,
        "--position-owner",
        args.position_owner,
        "--pool-address",
        args.pool_address,
        "--db",
        str(args.db),
        "--sdk-dir",
        str(args.sdk_dir),
    ]
    bin_command = [
        python,
        str(BIN_SCRIPT),
        "--rpc-url",
        args.rpc_url,
        "--pool-address",
        args.pool_address,
        "--lower-bin-id",
        str(args.lower_bin_id),
        "--upper-bin-id",
        str(args.upper_bin_id),
        "--db",
        str(args.db),
        "--sdk-dir",
        str(args.sdk_dir),
    ]

    started = time.monotonic()
    cycles = 0
    try:
        while time.monotonic() - started < args.duration_seconds:
            cycle_started = time.monotonic()
            cycles += 1
            print(f"collection_cycle={cycles}", flush=True)

            position_code = run_once(position_command)
            if position_code != 0:
                print(f"ERROR: position collection failed with exit code {position_code}", file=sys.stderr, flush=True)
                return position_code

            bin_code = run_once(bin_command)
            if bin_code != 0:
                print(f"ERROR: bin collection failed with exit code {bin_code}", file=sys.stderr, flush=True)
                return bin_code

            elapsed = time.monotonic() - cycle_started
            remaining = args.interval_seconds - elapsed
            if remaining > 0 and time.monotonic() - started < args.duration_seconds:
                time.sleep(min(remaining, max(0.0, args.duration_seconds - (time.monotonic() - started))))
    except KeyboardInterrupt:
        print("collection_interrupted=1", file=sys.stderr, flush=True)
        print(f"completed_cycles={cycles}", flush=True)
        return 130

    print(f"collection_complete=1", flush=True)
    print(f"completed_cycles={cycles}", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
