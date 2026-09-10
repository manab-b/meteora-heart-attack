from __future__ import annotations

import os
from pathlib import Path

from app.collector.live_sdk_ingest import _start_process


def test_start_process_runs_from_sdk_working_directory(tmp_path: Path):
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


def test_sdk_executable_path_is_absolute_before_sdk_cwd_is_used(tmp_path: Path):
    sdk_dir = tmp_path / "sdk"
    sdk_bin = (sdk_dir / "node_modules" / ".bin" / "tsx").resolve()

    assert sdk_bin.is_absolute()
    assert sdk_bin.parent.parent.parent == sdk_dir.resolve()
