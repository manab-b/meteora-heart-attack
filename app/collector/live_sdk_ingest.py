from __future__ import annotations

import argparse
import json
import os
import sqlite3
import subprocess
import sys
import threading
from pathlib import Path

from app.collector.bin_ingest import ingest_bin_observation
from app.collector.position_ingest import ingest_position_observation
from app.storage.migrations import initialize_database


def _reader(
    stream,
    handler,
    label: str,
) -> None:
    for raw_line in iter(stream.readline, ""):
        text = raw_line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
            if "error" in payload:
                print(f"[{label}] {text}", file=sys.stderr)
                continue
            handler(payload)
        except Exception as exc:
            print(f"[{label}] ingest error: {exc}", file=sys.stderr)
    stream.close()


def _start_process(command: list[str], env: dict[str, str], cwd: Path) -> subprocess.Popen[str]:
    return subprocess.Popen(
        command,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the read-only Meteora SDK collectors and ingest JSONL directly into SQLite."
    )
    parser.add_argument("--rpc-url", required=True)
    parser.add_argument("--position-owner", required=True)
    parser.add_argument("--pool-address", required=True)
    parser.add_argument("--lower-bin-id", required=True, type=int)
    parser.add_argument("--upper-bin-id", required=True, type=int)
    parser.add_argument("--db", type=Path, default=Path("meteora.db"))
    parser.add_argument("--interval-ms", type=int, default=30000)
    parser.add_argument("--sdk-dir", type=Path, default=Path("sdk"))
    args = parser.parse_args()

    if args.lower_bin_id > args.upper_bin_id:
        parser.error("--lower-bin-id must be <= --upper-bin-id")
    if args.interval_ms <= 0:
        parser.error("--interval-ms must be positive")

    db = sqlite3.connect(args.db, check_same_thread=False)
    initialize_database(db)
    lock = threading.Lock()

    def ingest_position(payload: dict) -> None:
        with lock:
            result = ingest_position_observation(db, payload)
        print(json.dumps({"type": "position", **result}, separators=(",", ":")), flush=True)

    def ingest_bin(payload: dict) -> None:
        with lock:
            ingest_bin_observation(db, payload)
            db.commit()
        print(
            json.dumps(
                {
                    "type": "bin",
                    "pool_address": payload.get("pool_address"),
                    "bin_id": payload.get("bin_id"),
                    "active_bin_id": payload.get("active_bin_id"),
                    "observed_at": payload.get("observed_at"),
                },
                separators=(",", ":"),
            ),
            flush=True,
        )

    env = os.environ.copy()
    env.update(
        {
            "RPC_URL": args.rpc_url,
            "POSITION_OWNER": args.position_owner,
            "POOL_ADDRESS": args.pool_address,
            "LOWER_BIN_ID": str(args.lower_bin_id),
            "UPPER_BIN_ID": str(args.upper_bin_id),
            "COLLECT_INTERVAL_MS": str(args.interval_ms),
        }
    )

    sdk_dir = args.sdk_dir.resolve()
    sdk_bin = sdk_dir / "node_modules" / ".bin" / "tsx"
    if not sdk_bin.exists():
        raise SystemExit(f"tsx executable not found: {sdk_bin}. Run npm install in {sdk_dir} first.")

    position_process = _start_process(
        [str(sdk_bin), "src/position_collector.ts", args.pool_address], env, sdk_dir
    )
    bin_process = _start_process(
        [str(sdk_bin), "src/bin_collector.ts"], env, sdk_dir
    )

    threads = [
        threading.Thread(target=_reader, args=(position_process.stdout, ingest_position, "positions"), daemon=True),
        threading.Thread(target=_reader, args=(bin_process.stdout, ingest_bin, "bins"), daemon=True),
        threading.Thread(target=_reader, args=(position_process.stderr, lambda x: print(f"[positions] {x}", file=sys.stderr), "positions-stderr"), daemon=True),
        threading.Thread(target=_reader, args=(bin_process.stderr, lambda x: print(f"[bins] {x}", file=sys.stderr), "bins-stderr"), daemon=True),
    ]
    for thread in threads:
        thread.start()

    try:
        while position_process.poll() is None and bin_process.poll() is None:
            position_process.wait(timeout=1)
    except KeyboardInterrupt:
        print("Stopping read-only SDK collectors", file=sys.stderr)
    finally:
        for process in (position_process, bin_process):
            if process.poll() is None:
                process.terminate()
        for process in (position_process, bin_process):
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
        db.close()

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
