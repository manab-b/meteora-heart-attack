from __future__ import annotations
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
    proc = subprocess.run(cmd, cwd=sdk_dir, env={"RPC_URL": rpc_url}, text=True,
                          capture_output=True, check=False)
    lines = proc.stdout.splitlines()
    cycle = ReadonlyCycle(connection).ingest(bin_lines=lines)
    return SdkRunResult(cycle, proc.returncode, proc.stderr)
