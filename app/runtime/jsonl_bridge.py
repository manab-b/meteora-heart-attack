from __future__ import annotations

import os
import sqlite3
import subprocess
from dataclasses import dataclass

from app.runtime.readonly_cycle import ReadonlyCycle, ReadonlyCycleResult


@dataclass(frozen=True)
class SdkRunResult:
    cycle: ReadonlyCycleResult
    returncode: int
    stderr: str


def _run_npm(
    sdk_dir: str,
    script: str,
    rpc_url: str,
    pools: list[str],
    extra_env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    cmd = ["npm", "run", script, "--", "--once", *pools]
    env = os.environ.copy()
    env["RPC_URL"] = rpc_url
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        cmd,
        cwd=sdk_dir,
        env=env,
        text=True,
        capture_output=True,
        check=False,
    )


def run_sdk_once(connection: sqlite3.Connection, sdk_dir: str, rpc_url: str, pools: list[str]) -> SdkRunResult:
    proc = _run_npm(sdk_dir, "collect", rpc_url, pools)
    cycle = ReadonlyCycle(connection).ingest(bin_lines=proc.stdout.splitlines())
    return SdkRunResult(cycle, proc.returncode, proc.stderr)


def run_sdk_positions_once(
    connection: sqlite3.Connection,
    sdk_dir: str,
    rpc_url: str,
    owner_address: str,
    pools: list[str],
) -> SdkRunResult:
    proc = _run_npm(
        sdk_dir,
        "collect:positions",
        rpc_url,
        pools,
        extra_env={"POSITION_OWNER": owner_address},
    )
    cycle = ReadonlyCycle(connection).ingest(position_lines=proc.stdout.splitlines())
    return SdkRunResult(cycle, proc.returncode, proc.stderr)
