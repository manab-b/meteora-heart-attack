from __future__ import annotations

import json
import os
import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Sequence


@dataclass(frozen=True)
class SdkCollectorResult:
    records: tuple[dict, ...]
    stderr: str
    returncode: int

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run_sdk_once(
    *,
    sdk_dir: str | Path,
    script: str,
    args: Sequence[str] = (),
    env: dict[str, str] | None = None,
    timeout_seconds: float = 60.0,
) -> SdkCollectorResult:
    """Run one read-only SDK collection and parse stdout JSONL.

    The inherited environment is preserved so RPC_URL/POSITION_OWNER and the
    normal Node runtime remain available. stderr is kept separate because the
    SDK uses it for diagnostics/errors and stdout is the machine-readable
    observation stream.
    """
    command = ["npm", "run", script, "--", "--once", *map(str, args)]
    merged_env = os.environ.copy()
    if env:
        merged_env.update(env)

    completed = subprocess.run(
        command,
        cwd=str(sdk_dir),
        env=merged_env,
        capture_output=True,
        text=True,
        timeout=timeout_seconds,
        check=False,
    )

    records: list[dict] = []
    for line in completed.stdout.splitlines():
        text = line.strip()
        if not text:
            continue
        try:
            payload = json.loads(text)
        except json.JSONDecodeError:
            continue
        if isinstance(payload, dict):
            records.append(payload)

    return SdkCollectorResult(tuple(records), completed.stderr, completed.returncode)
