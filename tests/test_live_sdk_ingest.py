from __future__ import annotations

import os
from pathlib import Path

import pytest

from app.collector.live_sdk_ingest import _start_process


def test_start_process_runs_relative_command_from_sdk_directory(tmp_path: Path):
    marker = tmp_path / "marker.txt"
    script = tmp_path / "write_marker.py"
    script.write_text(
        "from pathlib import Path\n"
        "Path('marker.txt').write_text('ok')\n",
        encoding="utf-8",
    )

    process = _start_process(
        [os.fspath(script)],
        os.environ.copy(),
        tmp_path,
    )
    stdout, stderr = process.communicate(timeout=5)

    assert process.returncode == 0, stderr
    assert stdout == ""
    assert marker.read_text(encoding="utf-8") == "ok"


def test_sdk_executable_is_resolved_before_cwd_change(tmp_path: Path):
    from app.collector.live_sdk_ingest import main

    sdk_dir = tmp_path / "sdk"
    executable = sdk_dir / "node_modules" / ".bin" / "tsx"
    executable.parent.mkdir(parents=True)
    executable.write_text("", encoding="utf-8")

    old_argv = __import__("sys").argv
    __import__("sys").argv = [
        "live_sdk_ingest",
        "--rpc-url",
        "https://example.invalid",
        "--position-owner",
        "owner",
        "--pool-address",
        "pool",
        "--lower-bin-id",
        "10",
        "--upper-bin-id",
        "9",
        "--sdk-dir",
        str(sdk_dir),
    ]
    try:
        with pytest.raises(SystemExit):
            main()
    finally:
        __import__("sys").argv = old_argv
