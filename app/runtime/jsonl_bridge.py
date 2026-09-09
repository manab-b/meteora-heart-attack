from __future__ import annotations
import os
import subprocess
import sqlite3
from dataclasses import dataclass
from app.runtime.readonly_cycle import ReadonlyCycle, ReadonlyCycleResult

@dataclass(frozen=True)
class SdkRunResult:
    cycle: ReadonlyCycleResult
    returncode: int
    stderr: str

def run_sdk_once(connection: sqlite3.Connection, sdk_dir: str, rpc_url: str, pools: list[str]) -> SdkRunResult:
    cmd = ["npm", "run", "collect", "--", "--once", *pools]
    env = os.environ.copy(); env["RPC_URL"] = rpc_url
    proc = subprocess.run(cmd, cwd=sdk_dir, env=env, text=True, capture_output=True, check=False)
    cycle = ReadonlyCycle(connection).ingest(bin_lines=proc.stdout.splitlines())
    return SdkRunResult(cycle, proc.returncode, proc.stderr)
